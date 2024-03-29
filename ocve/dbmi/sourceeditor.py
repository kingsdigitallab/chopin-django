__author__ = 'Elliott Hall'

# Functions and views for the specialised OCVE Source editor

from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.defaultfilters import register
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from ocve.bartools import *
from ocve.forms import *
from ocve.uitools import generateThumbnails
from .datatools import *


@register.filter()
def nbsp(value):
    return mark_safe(" ".join(value.split('&nbsp;')))


# New source that is being filled with metadata
def newsourceeditor(request, id=0):
    label = ''
    st = SourceType.objects.get(id=1)
    newS = None
    sourceInformation = None
    source = None
    try:
        newS = NewSource.objects.get(id=id)
        label = newS.library
    except ObjectDoesNotExist:
        newS = NewSource()
    if newS.sourcecreated > 0:
        source = Source.objects.get(id=newS.sourcecreated)
        sourceInformation = SourceInformation.objects.get(source=source)
        # dd=newS.sourcecreated
        # newsource=NewSource.objects.get(sourcecreated=1)
    else:
        source = Source.objects.create(sourcetype=st, label=label)
        source.save()
        sourcelegacy = SourceLegacy(
            source=source,
            cfeoKey=0,
            witnessKey=0,
            sourceDesc='',
            editstatus=EditStatus.objects.get(
                id=2),
            mellon=0,
            needsBarLines=1)
        sourcelegacy.save()
        sourceInformation = SourceInformation(source=source)
        # sourceInformation.sourcecode = newS.sourcecode
        newS.sourcecreated = source.id
        newS.save()

    accode = None
    pages = None
    wComps = None
    newpages = None
    if newS is not None:
        newpages = NewPageImage.objects.filter(source=newS)
    # if sourceInformation.accode is None:
    #     try:
    #         accode = AcCode.objects.get(accode=newS.sourcecode)
    #     except ObjectDoesNotExist:
    #         accode = AcCode.objects.create(accode=newS.sourcecode)
    #         accode.save()
    if accode is not None:
        sourceInformation.accode = accode
        sourceInformation.save()
    return sourceeditor(request, source, sourceInformation, newpages, wComps)


# Link the new source to the relevant work, and generate source compoennts
# if work has things like movements


def createDefaultComponents(source, w):
    wComps = WorkComponent.objects.filter(work=w)
    if wComps.count() == 0:
        # Create default work component for new empty work
        WorkComponent(
            work=w, orderno=1, label="Score", music=1,
            keymode=keyMode.objects.get(
                id=1), keypitch=keyPitch.objects.get(
                id=1), opus=Opus.objects.get(
                id=1)).save()
        wComps = WorkComponent.objects.filter(work=w)
    # Defaults for new source component
    piano = Instrument.objects.get(instrument='Piano')
    pianoScore = SourceComponentType.objects.get(type='Piano Score')
    orderno = 1
    newsourcecomponent = None
    for wc in wComps:
        # Create a new source component for each work component
        if SourceComponent.objects.filter(
                sourcecomponent_workcomponent__workcomponent=wc,
                source=source).count() == 0:
            sc = SourceComponent.objects.create(
                sourcecomponenttype=pianoScore,
                source=source,
                orderno=orderno,
                label=wc.label,
                instrumentnumber=1)
            # Attach
            SourceComponent_WorkComponent.objects.create(
                sourcecomponent=sc, workcomponent=wc)
            SourceComponent_Instrument.objects.create(
                sourcecomponent=sc, instrument=piano)
            newsourcecomponent = sc
        else:
            newsourcecomponent = SourceComponent.objects.filter(
                sourcecomponent_workcomponent__workcomponent=wc,
                source=source)[0]
    return newsourcecomponent


# Editing a source that already exists
def existingsourceeditor(request, id):
    try:
        source = Source.objects.get(id=id)
        sourceInformation = SourceInformation.objects.get(source=source)
        # pages = PageImage.objects.filter(
        # page__sourcecomponent__source=source).order_by('page__orderno')
        workcomponents = WorkComponent.objects.filter(
            sourcecomponent_workcomponent__sourcecomponent__source=source
        ).distinct()
        # Added in case new pages have been uploaded to this existing source
        try:
            newpageimages = NewPageImage.objects.filter(
                source=NewSource.objects.get(
                    sourcecreated=source.id), linked=0)
        except ObjectDoesNotExist:
            newpageimages = None
        return sourceeditor(
            request,
            source,
            sourceInformation,
            newpageimages,
            workcomponents)
    except ObjectDoesNotExist:
        # standard error page?
        return HttpResponse("ERROR in existingsourceeditor")


# Reset the orderno field in page using its label.


def reorderPagesByDefault(pageimages):
    for pi in pageimages:
        p = pi.page
        try:
            p.orderno = int(p.label)
            p.save()
        except ValueError:
            pass


# Reorder the pages in a source based on the label.  Very crude but good
# to correct earlier errors


def defaultpageorder(request, id):
    source = Source.objects.get(id=id)
    pageimages = PageImage.objects.filter(
        page__sourcecomponent__source=source).order_by(
        'sourcecomponent_orderno', 'page__orderno')
    reorderPagesByDefault(pageimages)
    return HttpResponseRedirect("/ocve/sourceeditor/" + id + "/")


@csrf_exempt
def updatecopyright(request):
    copyright = False
    try:
        copyright = request.POST["copyright"]
        copyright = True
    except MultiValueDictKeyError:
        pass
    try:
        pageimage_id = request.POST["pageimage_id"]
        pi = PageImage.objects.get(id=int(pageimage_id))
        pi.copyright = copyright
        pi.save()
        result = "Copyright Updated"
    except ObjectDoesNotExist:
        result = "ERROR in updatecopyright"
    return result


@csrf_exempt
def updatepagetype(request, id):
    result = ""
    try:
        p = Page.objects.get(id=id)
        tid = request.POST["id_pagetype"]
        Type = PageType.objects.get(id=int(tid))
        p.pagetype = Type
        p.save()
        result = "Type updated to" + Type.type
    except ObjectDoesNotExist:
        result = "ERROR in pagetype update"
    return HttpResponse(result)


# The DBMi editor view for altering source structure
# This view is used for new and existing sources


def sourceeditor(
        request,
        source,
        sourceInformation,
        newpageimages,
        workcomponents):
    sourceForm = SourceForm(instance=source)
    sourceInformationForm = SourceInformationForm(instance=sourceInformation)
    scForm = SourceComponentForm()
    pageimages = PageImage.objects.filter(
        page__sourcecomponent__source=source).order_by('page__orderno')
    instruments = Instrument.objects.all()
    sourcecomponents = SourceComponent.objects.filter(
        source=source).order_by('orderno')
    works = Work.objects.all()
    opus = source.getOpusLabel()
    pagetypes = PageType.objects.all()
    return render(request, ('dbmi/sourceeditor.html',
                            {'works': works,
                             'pagetypes': pagetypes,
                             'instruments': instruments,
                             'scForm': scForm,
                             'pageimages': pageimages,
                             'newpageimages': newpageimages,
                             'workcomponents': workcomponents,
                             'sourcecomponents': sourcecomponents,
                             'sourceForm': sourceForm,
                             'sourceInformationForm': sourceInformationForm,
                             'opus': opus,
                             'IMAGE_SERVER_URL': settings.IMAGE_SERVER_URL,
                             },
                            )
                  )


@csrf_exempt
def createfrontmatter(request, sourceid):
    s = Source.objects.get(id=sourceid)
    return createnonmusiccomponent(request, 'Front matter', 1, s)


@csrf_exempt
def createendmatter(request, sourceid):
    s = Source.objects.get(id=sourceid)
    comps = SourceComponent.objects.filter(source=s).order_by('-orderno')
    if comps.count > 0:
        orderno = comps[0].orderno + 1
    else:
        orderno = 1
    return createnonmusiccomponent(request, 'End matter', orderno, s)


@csrf_exempt
def createnonmusiccomponent(request, label, orderno, source):
    noinstrument = Instrument.objects.get(instrument='None')
    sctype = SourceComponentType.objects.get(type='Non-music')
    sc = SourceComponent(
        source=source,
        label=label,
        orderno=orderno,
        sourcecomponenttype=sctype)
    sc.save()
    SourceComponent_Instrument(
        instrument=noinstrument,
        sourcecomponent=sc).save()
    return HttpResponse(label + " created")


@csrf_exempt
def createsourcecomponent(request, sourceid):
    source = Source.objects.get(id=sourceid)
    sc = SourceComponent(source=source)
    piano = Instrument.objects.get(instrument='Unspecified')
    sctype = SourceComponentType.objects.get(type='Piano Score')
    sc.sourcecomponenttype = sctype
    sc.save()
    SourceComponent_Instrument(instrument=piano, sourcecomponent=sc).save()
    return editsourcecomponent(request, sc)


@csrf_exempt
def editexistingsourcecomponent(request, id):
    sc = SourceComponent.objects.get(id=id)
    return editsourcecomponent(request, sc)


@csrf_exempt
def editsourcecomponent(request, sc):
    source = sc.source
    work = source.getWork()
    workcomponents = WorkComponent.objects.filter(work=work)
    currentwc = None
    comps = WorkComponent.objects.filter(
        sourcecomponent_workcomponent__sourcecomponent=sc)
    if comps.count() > 0:
        currentwc = comps[0]
    scf = SourceComponentForm(instance=sc)
    curinstrument = Instrument.objects.get(instrument='Piano')
    if Instrument.objects.filter(sourcecomponent=sc).count() > 0:
        curinstrument = Instrument.objects.filter(sourcecomponent=sc)[0]
    instruments = Instrument.objects.filter()
    # If changed
    # return existingsourceeditor(request, id)
    return render(request, 'dbmi/sourcecomponent.html',
                            {'sc': sc,
                             'scf': scf,
                             'workcomponents': workcomponents,
                             'currentwc': currentwc,
                             'instruments': instruments,
                             'curinstrument': curinstrument},
                            )

@ csrf_exempt
def deletesourcecomponent(request, id):
    sc = SourceComponent.objects.get(id=id)
    sourceid = sc.source.id
    if PageImage.objects.filter(page__sourcecomponent=sc).count() == 0:
        sc.delete()
    return HttpResponseRedirect("/ocve/sourceeditor/" + str(sourceid) + "/")


@csrf_exempt
def savesourcecomponent(request, id):
    scform = SourceComponentForm(request.POST,
                                 instance=SourceComponent.objects.get(id=id))
    sc = scform.save()
    try:
        wcid = int(request.POST["id_workcomponent"])
        if wcid > 1:
            wc = WorkComponent.objects.get(id=wcid)
            scwc = SourceComponent_WorkComponent.objects.filter(
                sourcecomponent=sc)
            if scwc.count() > 0:
                link = scwc[0]
                link.workcomponent = wc
                link.save()
            elif wcid > 1:
                SourceComponent_WorkComponent(
                    sourcecomponent=sc, workcomponent=wc).save()
    except MultiValueDictKeyError:
        pass
    try:
        iid = request.POST["id_instrument"]
        instrument = Instrument.objects.get(id=iid)
        scic = SourceComponent_Instrument.objects.filter(sourcecomponent=sc)
        if scic.count() > 0:
            link = scic[0]
            link.instrument = instrument
            link.save()
        else:
            SourceComponent_Instrument(
                sourcecomponent=sc, instrument=instrument).save()
    except MultiValueDictKeyError:
        pass
    return HttpResponseRedirect(
        "/ocve/sourceeditor/" + str(sc.source.id) + "/")


# Remove superflous html tags added by TinyMCE
def cleanHTML(label):
    label = label.replace(
        '<p>',
        '').replace(
        '<span>',
        '').replace(
        '</span>',
        '')
    label = label.replace('</p>', '').replace('\r', '').replace('\n', '')
    label = label.replace(
        '<div>',
        '').replace(
        '</div>',
        '').replace(
        '<br />',
        '').replace(
        "<p class=\"BodyAA\">",
        "")
    return label


# Save new source
@csrf_exempt
def saveSource(request, id):
    msg = ''
    # Populate source from request
    sourcef = SourceForm(request.POST, instance=Source.objects.get(id=id))
    source = sourcef.save()
    try:
        source.label = cleanHTML(source.label)
        source.cfeolabel = cleanHTML(source.cfeolabel)
    except MultiValueDictKeyError:
        pass
    source.save()
    # Create source information if source is brand new
    try:
        SourceInformation.objects.get(source=source)
    except ObjectDoesNotExist:
        SourceInformation(source=source).save()

    try:
        workid = int(request.POST["work_id"])
        w = Work.objects.get(id=workid)
        if source.getWork() != w:
            # New Modified source,
            # Get pages, if they exist (may be new source)
            oldWork = source.getWork()
            sourcePages = source.getPages()
            newsourcecomponent = createDefaultComponents(source, w)
            # Add pages to sourcecomponent corresponding to first work
            # component
            if newsourcecomponent is not None:
                for sp in sourcePages:
                    # If this attached to opus e.g. not front matter
                    if SourceComponent_WorkComponent.objects.filter(
                            sourcecomponent=sp.sourcecomponent).count() > 0:
                        sp.sourcecomponent = newsourcecomponent
                        sp.save()
                # Delete old components
                oldcomponents = SourceComponent.objects.filter(
                    source=source,
                    sourcecomponent_workcomponent__workcomponent__work
                    =oldWork).delete()

    except MultiValueDictKeyError:
        pass
    try:
        newsource = NewSource.objects.get(sourcecreated=id)
        sourcenewid = newsource.pk
        # return HttpResponseRedirect('/ocve/sourceeditor/new/' +
        # str(newsource.pk) + '/#sourceMetadata')
        return newsourceeditor(request, newsource.pk)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(
            '/ocve/sourceeditor/' +
            str(id) +
            '/#sourceMetadata')


# Remove unneeded HTML elements added by TinyMCE from souce information fields


def cleanSourceInformationHTML(si):
    # Paragraph tags
    if si.title is not None:
        si.title = cleanHTML(si.title)
    if si.copyright is not None:
        si.copyright = cleanHTML(si.copyright).replace('&copy; ', '')
    if si.publicationtitle is not None:
        si.publicationtitle = cleanHTML(si.publicationtitle)
    return si


# New source information


@csrf_exempt
def saveSourceInformation(request, id):
    # source=SourceForm(request.POST)
    sinfo = SourceInformationForm(
        request.POST,
        instance=SourceInformation.objects.get(
            id=id))
    # Check the form validates
    if len(sinfo.errors) > 0:
        return HttpResponse(
            "<html><body><h1>Error saving source information</h1>" + str(
                sinfo.errors) + "</body></html>")
    else:
        sourceInformation = sinfo.save(commit=False)
        try:
            for changed in sinfo.changed_data:
                if changed == 'printingmethod':
                    methods = sinfo.cleaned_data['printingmethod']
                    if methods.count() > 0:
                        # Remove existing methods, replace with changed set
                        SourceInformation_PrintingMethod.objects.filter(
                            sourceinformation=sourceInformation).delete()
                    for m in methods:
                        SourceInformation_PrintingMethod(
                            sourceinformation=sourceInformation,
                            printingmethod=m).save()
        except MultiValueDictKeyError:
            pass
        # Check if new authority list variables have been filled in, create and
        # link as necessary
        try:
            newmethod = request.POST["newmethod"]
            if newmethod is not None and len(newmethod) > 0:
                newm = PrintingMethod(method=newmethod)
                newm.save()
                SourceInformation_PrintingMethod(
                    sourceinformation=sourceInformation,
                    printingmethod=newm).save()
        except MultiValueDictKeyError:
            pass
        try:
            newarchive = request.POST["newarchive"]
            if newarchive is not None and len(newarchive) > 0:
                newa = Archive(name=newarchive)
                newa.save()
                sourceInformation.archive = newa
        except MultiValueDictKeyError:
            pass
        try:
            newaccode = request.POST["newaccode"]
            if newaccode is not None and len(newaccode) > 0:
                addAcCode(newaccode, sourceInformation)
        except MultiValueDictKeyError:
            pass
        # Extra widgets for adding formatting to dedicatee/publishers
        # and preserving dedicatee alternate spellings
        try:
            altDT = int(request.POST["altDedicateeType"])
            altPT = int(request.POST["altPublisherType"])
            if altDT is not None and altDT > 0:
                altD = request.POST["altDedicatee"]
                if altDT == 1:
                    # New
                    d = Dedicatee(dedicatee=altD)
                    d.save()
                    sourceInformation.dedicatee = d
                    sourceInformation.save()
                if altDT == 2:
                    # Alternate
                    altDedicatee = Dedicatee(
                        dedicatee=altD,
                        alternateOf=sourceInformation.dedicatee)
                    altDedicatee.save()
                    sourceInformation.dedicatee = altDedicatee
                    sourceInformation.save()
                if altDT == 3:
                    # Overwrite
                    d = sourceInformation.dedicatee
                    d.dedicatee = altD
                    d.save()
            if altPT is not None and altPT > 0:
                altP = request.POST["altPublisher"]
                if altPT == 1:
                    p = Publisher(publisher=altP)
                    p.save()
                    sourceInformation.publisher = p
                    sourceInformation.save()
                if altPT == 3:
                    p = sourceInformation.publisher
                    p.publisher = altP
                    p.save()
        except MultiValueDictKeyError:
            pass
        sourceInformation = cleanSourceInformationHTML(sourceInformation)
        sourceInformation.save()
    source = sourceInformation.source
    return HttpResponseRedirect(
        '/ocve/sourceeditor/' + str(source.id) + '/#sourceInformationMetadata')


@csrf_exempt
def updateComponentOrder(request):
    msg = ''
    try:
        scString = request.POST['sckeys']
        scKeys = scString.split(",")
        x = 1
        for sc in scKeys:
            key = sc.replace('sc ', '')
            try:
                sourcecomponent = SourceComponent.objects.get(id=int(key))
                sourcecomponent.orderno = x
                sourcecomponent.save()
                x += 1
            except ObjectDoesNotExist:
                pass
    except MultiValueDictKeyError:
        pass
    return HttpResponse(msg)


@csrf_exempt
def savePage(request):
    msg = request.POST['value']
    is_newpage = str(request.POST['is_newpage'])
    is_textlabel = str(request.POST['is_textlabel'])
    if is_textlabel == 'true':
        # Update the text label for a page
        msg = msg.replace('-', '\u2013')
        spageimage = PageImage.objects.get(id=int(request.POST['id']))
        spageimage.textlabel = msg
        spageimage.save()
    # return HttpResponse(str(is_newpage))
    list1 = re.split('\W+', request.POST['idsc'])
    sc = SourceComponent.objects.get(id=int(list1[1]))
    scorderno = int(request.POST['numsc']) + 1
    if scorderno > 0:
        sc.orderno = scorderno
        sc.save()
    # list2 = re.split(r'\W+', msg)
    list2 = re.findall(r"[\w\[\]]+", msg)
    pagenum = 0
    startbar = 0
    endbar = 0
    if re.match('p\.*\s*(\S+)', msg):
        pagenum = re.search('p\.*\s*(\S+)', msg).group(1)
    if re.match('.*bs\s*(\d+)[-|\u2013](\d+).*', msg):
        numbers = re.search('.*bs\s*(\d+)[-|\u2013](\d+).*', msg)
        startbar = numbers.group(1)
        endbar = numbers.group(2)
    if is_newpage == 'true':
        np = NewPageImage.objects.get(id=int(request.POST['id']))
        jp = 'newjp2/' + str(np.id) + '.jp2'
        if np.linked > 0:  # the new page was already saved
            spageimage = PageImage.objects.get(id=np.linked)
            # saveBars(msg, spageimage)
            if startbar > 0:
                spageimage.startbar = startbar
            if endbar > 0:
                spageimage.endbar = endbar
            spageimage.save()
            spage = Page.objects.get(id=spageimage.page.id)
            spage.label = pagenum
            spage.orderno = int(request.POST['idnum'])
            spage.sourcecomponent = sc
            spage.save()
        else:
            spage = Page(
                label=pagenum,
                orderno=int(
                    request.POST['idnum']),
                sourcecomponent=sc)
            spage.save()
            spageimage = PageImage(
                page=spage,
                corrected=0,
                height=np.height,
                width=np.width)
            if startbar > 0:
                spageimage.startbar = startbar
            if endbar > 0:
                spageimage.endbar = endbar
            spageimage.save()
            pagelegacy = PageLegacy(pageimage=spageimage,
                                    jp2='newjp2/' + str(np.id) + '.jp2',
                                    editstatus=EditStatus.objects.get(id=2),
                                    cropCorrected=1)
            pagelegacy.save()
        np.linked = spageimage.id
        # saveBars(msg, np)
        np.startbar = startbar
        np.endbar = endbar
        np.save()
    else:
        spageimage = PageImage.objects.get(id=int(request.POST['id']))
        # saveBars(msg, spageimage)
        if startbar > 0:
            spageimage.startbar = startbar
        if endbar > 0:
            spageimage.endbar = endbar
        spageimage.save()
        spage = Page.objects.get(id=spageimage.page.id)
        if pagenum > 0:
            spage.label = pagenum
        spage.orderno = int(request.POST['idnum'])
        spage.sourcecomponent = sc
        spage.save()

    return HttpResponse(msg)


@csrf_exempt
def updatepageindex(request):
    try:
        msg = request.POST['id']
        list1 = re.split('\W+', request.POST['idsc'])
        sc = SourceComponent.objects.get(id=int(list1[1]))
        sc.orderno = int(request.POST['numsc']) + 1
        sc.save()
        is_newpage = str(request.POST['is_newpage'])
        if is_newpage == 'true':
            np = NewPageImage.objects.get(id=int(request.POST['id']))
            if np.linked > 0:  # the new page was already saved
                spageimage = PageImage.objects.get(id=np.linked)
                spage = Page.objects.get(id=spageimage.page.id)
                spage.orderno = int(request.POST['idnum'])
                spage.sourcecomponent = sc
                spage.save()
            else:
                spage = Page(
                    orderno=int(
                        request.POST['idnum']),
                    sourcecomponent=sc)
                spage.save()
                spageimage = PageImage(
                    page=spage,
                    startbar=0,
                    endbar=0,
                    corrected=0,
                    height=0,
                    width=np.width)
                spageimage.save()
                pagelegacy = PageLegacy(pageimage=spageimage,
                                        jp2='newjp2/' + str(np.id) + '.jp2',
                                        editstatus=EditStatus.objects.get(
                                            id=2),
                                        cropCorrected=1)
                pagelegacy.save()
            np.linked = spageimage.id
            np.save()
        else:
            spageimage = PageImage.objects.get(id=int(request.POST['id']))
            spageimage.save()
            spage = Page.objects.get(id=spageimage.page.id)
            spage.orderno = int(request.POST['idnum'])
            spage.sourcecomponent = sc
            spage.save()
    except MultiValueDictKeyError:
        msg = "ID missing"
    return HttpResponse(msg)


@csrf_exempt
def deletepage(request, id):
    try:
        pi = PageImage.objects.get(id=id)
        sourceid = pi.page.sourcecomponent.source.id
        for np in NewPageImage.objects.filter(linked=id):
            np.linked = 0
            np.save()

        pi.delete()
        return existingsourceeditor(request, sourceid)
    except ObjectDoesNotExist:
        return HttpResponse("Page with ID does not exist")


@csrf_exempt
# Delete a source, and delete any attached jp2s
def deletesource(request, id):
    s = Source.objects.get(id=int(id))
    log = ''
    # delete any attached jp2s
    # Temporarily disabled because of source cloning
    # for pi in PageImage.objects.filter(page__sourcecomponent__source=s,
    # versionnumber=1).order_by("page"):
    # jp2=pi.getJP2Path()
    # if re.search('UNVERIFIED',jp2) is None:
    #    try:
    #        log+='<br/> Attempting to delete jp2 '+str(
    #        settings.IMAGEFOLDER+jp2)
    #        os.remove(settings.IMAGEFOLDER+jp2)
    #    except (IOError, OSError), e:
    #         log+=('<br/> Error removing TIFF [%s], Reason: %s' % (jp2, e))
    # else:
    #    log+='<br/> Unverified image skipped'
    s.delete()
    # 28-1-W_USCu_b1_p20_no14
    # return HttpResponseRedirect('/ocve/dbmi/')
    return render(request, ('dbmi/sourcedelete.html', {'log': log}))

                  # Clone a page, usually for pages that span source components
                  # NOTE: Clones page,pageimage,pagelegacy ONLY, not bar
                  # informtation

@ csrf_exempt
def clonepage(request, id):
    try:
        # Get pageimage to clone
        sourcepageimage = PageImage.objects.get(id=id)
        sourcedict = model_to_dict(sourcepageimage)

        # Clone page
        sourcepage = sourcepageimage.page
        sourcepagedict = model_to_dict(sourcepage)
        sc = sourcepage.sourcecomponent
        sourcepagedict['sourcecomponent'] = sc
        sourcepagedict['pagetype'] = sourcepage.pagetype
        newpage = Page(**sourcepagedict)
        newpage.id = None
        newpage.save()
        sourcedict['page'] = newpage
        newpageimage = PageImage(**sourcedict)
        newpageimage.id = None
        newpageimage.save()

        # Clone Pagelegacy
        legacies = PageLegacy.objects.filter(pageimage=sourcepageimage)
        if legacies.count() > 0:
            legacy = legacies[0]
            legacydict = model_to_dict(legacy)
            legacydict['pageimage'] = sourcepageimage
            legacydict['editstatus'] = legacy.editstatus
            newpl = PageLegacy(**legacydict)
            newpl.id = None
            newpl.pageimage = newpageimage
            newpl.save()

        return HttpResponseRedirect(
            '/ocve/sourceeditor/' + str(newpage.sourcecomponent.source.id))

    except ObjectDoesNotExist:
        return HttpResponse("PAGEIMAGE DOES NOT EXIST")


# Clone a source


@csrf_exempt
def clonesource(request, id):
    source = Source.objects.get(id=int(id))
    newSourceComponents = {}
    newPageImages = {}
    pageimages = PageImage.objects.filter(page__sourcecomponent__source=source)
    for pi in pageimages:
        try:
            # Already cloned
            pi = newPageImages[str(pi.id)]
        except KeyError:
            newPageImages[str(pi.id)] = pi
            legacy = PageLegacy.objects.filter(pageimage=pi)
            originalpageimageid = pi.id
            pl = None
            if legacy.count() > 0:
                pl = legacy[0]
            pi.pk = None
            pi.save()
            if pl is not None:
                # Clone page legacy and link
                pl.pk = None
                pl.save()
                pl.pageimage = pi
                pl.save()
            p = pi.page
            # Get source components
            comp = None
            comps = SourceComponent.objects.filter(page=p)
            for c in comps:
                try:
                    comp = newSourceComponents[str(c.id)]
                except KeyError:
                    newSourceComponents[str(c.id)] = c
                    cid = c.id
                    # New Source component
                    c.pk = None
                    c.save()
                    # Clone intersection links to work
                    scwc = SourceComponent_WorkComponent.objects.filter(
                        sourcecomponent_id=cid)
                    for link in scwc:
                        SourceComponent_WorkComponent(
                            sourcecomponent=c,
                            workcomponent=link.workcomponent).save()
                    comp = c
            # clone pages
            p.pk = None
            if comp is not None:
                p.sourcecomponent = comp
            p.save()
            pi.page = p
            pi.save()

        # Link new pi to region
        regions = BarRegion.objects.filter(pageimage_id=originalpageimageid)
        if regions.count() > 0:
            for r in regions:
                # Original region id
                rid = r.id
                # For each region
                r.pk = None
                r.save()
                # Clone bars
                bars = Bar.objects.filter(bar_barregion__barregion_id=rid)
                for b in bars:
                    b.pk = None
                    b.save()
                    Bar_BarRegion(bar=b, barregion=r).save()
                r.pageimage = pi
                r.save()

    # Clones source information
    try:
        info = SourceInformation.objects.get(source=source)
        info.pk = None
        info.save()
    except ObjectDoesNotExist:
        info = SourceInformation()
    # New source, link to top of chain
    source.pk = None
    source.save()
    generateThumbnails([source])
    info.source = source
    # Reset accode
    info.accode = AcCode.objects.get(id=1)
    info.save()
    for sc in newSourceComponents:
        newSourceComponents[sc].source = source
        newSourceComponents[sc].save()

    return HttpResponseRedirect('/ocve/sourceeditor/' + str(source.id))

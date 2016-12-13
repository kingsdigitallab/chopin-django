__author__ = 'Elliott Hall'

from xlwt import Workbook, easyxf
from xlrd import open_workbook
import numpy as np
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

from ocve.models import *
from ocve.bartools import BarRegionThumbnail



# *** Spine Views ***
# Export Spines of a work to an Excel workbook for editing
def exportXLS(request, id):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    cursor = connection.cursor()
    if int(id) == 0:
        # Posthumous case
        sources = Source.objects.filter(
            sourcecomponent__sourcecomponent_workcomponent__workcomponent__work__workcollection=3).order_by(
            'sourcecomponent__sourcecomponent_workcomponent__workcomponent__work', 'orderno').distinct()
        response['Content-Disposition'] = 'attachment; filename="Posthumous_Spine.xls"'
        label = 'Posthumous Spines'
    else:
        work = Work.objects.get(id=id)
        sources = Source.objects.filter(
            sourcecomponent__sourcecomponent_workcomponent__workcomponent__work=work).order_by('orderno').distinct()
        response['Content-Disposition'] = 'attachment; filename="Spine' + str(work.id) + '.xls"'
        label = work.label + ' Spines'
    # Create Workbook and single sheet for all spines
    book = Workbook(encoding='utf-8')
    label = label.replace('[', '').replace(']', '')
    if len(label) > 20:
        label = label[:20] + '...'
    sheet = book.add_sheet(label)

    # Different colour backgrounds to distinguish between movements in the workbook
    mvtFormats = [
        easyxf('font: color red;'),
        easyxf('font: color blue;'),
        easyxf('font: color green;'),
        easyxf('font: color gold;'),
        easyxf('font: color brown;'),
    ]
    sourceRow = sheet.row(0)
    codeRow = sheet.row(1)
    colIndex = 0
    mvtIndexes = []

    for s in sources:
        #Write the first two rows, containing source keys and ac codes
        code = s.getAcCode()
        sourceRow.write(colIndex, str(s.id))
        codeRow.write(colIndex, code, )

        mvtIndexes.append(0)
        mvtFormatIndex = 0
        curSourceComponent = 0
        #Write all spines for source
        sql="SELECT DISTINCT ocve_bar.barlabel,ocve_barspine.bar_id,ocve_barspine.orderno,ocve_barspine.source_id,ocve_barspine.implied,ocve_barspine.sourcecomponent_id FROM ocve_bar,ocve_barspine where ocve_bar.id=ocve_barspine.bar_id and source_id="+str(s.id)+" order by ocve_barspine.orderno"
        cursor.execute(sql)
        for row in cursor.fetchall():
            bar=row[0]
            r=int(row[2])+1
            sourcecomponent=row[5]
            if row[4] == 1:
                bar = bar + '(I)'
            if curSourceComponent == 0:
                 curSourceComponent = sourcecomponent
            elif curSourceComponent != sourcecomponent:
            #Change style
                if mvtFormatIndex == 4:
                    mvtFormatIndex = 0
                else:
                    mvtFormatIndex += 1
                curSourceComponent = sourcecomponent
            style = mvtFormats[mvtFormatIndex]
            sheet.write(r, colIndex, bar, style)

        colIndex += 1
        
    #Finish and write to stream
    book.save(response)
    return response


# Generates a positional map for every bar in a work
# This allows the precise region to be found on import without having the source component id
def getCellMap(sourceid):
    cursor = connection.cursor()
    #barregion,bar,sourcecomponent,source
    #order by source.orderno,sourceomponent,orderno,bar
    sql = "select distinct b.barlabel,b.id,p.id,sc.id,s.id,s.orderno as source_order,sc.orderno,p.orderno,b.barnumber "
    sql += "from ocve_bar as b,ocve_bar_barregion as bbr,ocve_barregion as br,ocve_page as p,ocve_pageimage as pi,"
    sql += "ocve_sourcecomponent as sc,ocve_source as s "
    sql += "where b.id=bbr.bar_id and bbr.barregion_id=br.id and br.pageimage_id=pi.id and pi.page_id=p.id "
    sql += "and p.sourcecomponent_id=sc.id and sc.source_id=s.id and s.id=" + str(sourceid)
    sql += " order by s.orderno,sc.orderno,p.orderno,b.barnumber;"
    dt = np.dtype(
        [('barlabel', np.str_, 10), ('bar_id', np.int_), ('page_id', np.int_), ('sourcecomponent_id', np.int_),
         ('source_id', np.int_), ('assigned', np.bool_)])
    cursor.execute(sql)
    cellmap = np.ndarray(shape=(cursor.rowcount,), dtype=dt)
    x = 0
    for row in cursor.fetchall():
        cellmap[x]['barlabel'] = row[0]
        cellmap[x]['bar_id'] = row[1]
        cellmap[x]['page_id'] = row[2]
        cellmap[x]['sourcecomponent_id'] = row[3]
        cellmap[x]['source_id'] = row[4]
        cellmap[x]['assigned'] = False
        x += 1

    return cellmap


# @csrf_exempt
# def importXLS(request):
#     workid = int(request.POST['workid'])
#     work = Work.objects.get(id=workid)
#
#     result = "File Uploaded"
#     if request.method == 'POST':
#         try:
#             workid = int(request.POST['workid'])
#             work = Work.objects.get(id=workid)
#             #response.write('<h1>'+work.label+'</h1><table border=\"1\">')
#             BarSpine.objects.filter(
#                 source__sourcecomponent__sourcecomponent_workcomponent__workcomponent__work=work).delete()
#             #Load worksheet
#             wb = open_workbook(file_contents=request.FILES['uploadFile'].read())
#
#             for s in wb.sheets():
#                 #For each column (source)
#                 for col in range(s.ncols):
#                     #For each row in column
#                     for row in s.col(col):
#                         #Get cell


def getCellFromMap(barvalue, implied, barmap, lastindex):
    #Since most pieces are linear, use lastindex for a guess before iteration
    guess = lastindex + 1
    # if guess < len(barmap) and barmap[guess]['barlabel'] == barvalue and barmap[guess]['assigned'] == False:
    #     barmap[guess]['assigned'] = True
    #     return [guess,barmap[guess]]
    # else:
    #     #Start again
    startIndex=0
    for index in range(startIndex,len(barmap)):
        cell= barmap[index]
        if cell['barlabel'] == barvalue and (cell['assigned'] == False or implied == 1):
            #Don't count as assigned if implied
            if implied == 0:
                cell['assigned'] = True
            return [index, cell]
    return None


@csrf_exempt
def importXLS(request):
    workid = int(request.POST['workid'])
    work = Work.objects.get(id=workid)
    cursor = connection.cursor()
    result = "<h2>Log</h2>"
    if request.method == 'POST':
        try:
            workid = int(request.POST['workid'])
            work = Work.objects.get(id=workid)
            #response.write('<h1>'+work.label+'</h1><table border=\"1\">')
            BarSpine.objects.filter(
                source__sourcecomponent__sourcecomponent_workcomponent__workcomponent__work=work).delete()
            #wb = open_workbook(request.FILES['uploadFile'])
            wb = open_workbook(file_contents=request.FILES['uploadFile'].read())
            spines = []
            #get bar map

            for s in wb.sheets():
                for col in range(s.ncols):
                    source_id = s.cell(0, col).value
                    if source_id > 1:
                        barmap = getCellMap(source_id)
                        lastindex = 0
                        for row in range(2, s.nrows):
                            value = str(s.cell(row, col).value)
                            #response.write('<td>'+value+'</td>')
                            try:
                                if len(value) > 0 and value != ' ':
                                    implied = 0
                                    value = value.replace('.0', '')
                                    if '(I)' in value:
                                        #Implied repeat, note and clean
                                        value = value.replace('(I)', '')
                                        implied = 1
                                    try:
                                        results = getCellFromMap(value, implied, barmap, lastindex)
                                        if results != None:
                                            cell = results[1]
                                            lastindex = results[0]
                                            # bs = BarSpine()
                                            # bs.bar_id = cell['bar_id']
                                            # bs.implied = implied
                                            orderno = row - 1
                                            # bs.label = orderno
                                            # bs.orderno = orderno
                                            # bs.source_id = source_id
                                            # bs.sourcecomponent_id = cell['sourcecomponent_id']
                                            # bs.save()
                                            spines.append([orderno,cell['bar_id'],orderno,source_id,implied,cell['sourcecomponent_id']])
                                        else:
                                            result += "<p>Bar value "+str(value)+" at row " + str(row) + " col " + str(
                                                col) + " not found in source "+str(source_id)+", ignored</p>"
                                    except IndexError:
                                        col
                            except ObjectDoesNotExist:
                                skip = 0
                                #response.write('</tr>')
                                #response.write('</table></body></html>')
                    else:
                        result += "<p>Source key" + str(s.cell(0, col).value) + " not found, column ignored</p>"
            #Insert Spines
            args_str = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s,%s)", x) for x in spines)
            cursor.execute("INSERT INTO ocve_barspine (label,bar_id,orderno,source_id,implied,sourcecomponent_id) VALUES " + args_str)
        except ObjectDoesNotExist:
            result = "Parse Error"
    return render_to_response('dbmi/importresult.html',
                              {'result': result, 'work': work})  #Creates a default spine for a source.


def generateSpine(source):
    regions = BarRegion.objects.filter(pageimage__page__sourcecomponent__source=source).order_by(
        'pageimage__page__sourcecomponent__orderno', 'pageimage__page__orderno', 'bar').distinct()
    x = 1
    for r in regions:
        for bar in r.bar.all():
            bs = BarSpine(label=x, orderno=x, bar=bar, source=source, sourcecomponent=r.pageimage.page.sourcecomponent)
            bs.save()
            x += 1


#get a particular spine from a work
def getSpinesByWork(work, orderno, range=1):
    #if range > 1:
    #    spines = BarSpine.objects.filter(orderno__range=(orderno,orderno+range),source__ocve=1,source__sourcecomponent__sourcecomponent_workcomponent__workcomponent__work=work).order_by('ocve_barSpine.source_id').distinct()
    #else:
    spines = BarSpine.objects.filter(orderno=orderno, source__ocve=1,
                                     source__sourcecomponent__sourcecomponent_workcomponent__workcomponent__work=work).distinct()
    return spines


#Remove the bar spines for a source and then rebuild from default
def deleteSourceSpines(request, id):
    try:
        s = Source.objects.get(id=id)
        BarSpine.objects.filter(source=s).delete()
        generateSpine(s)
    except ObjectDoesNotExist:
        pass
    return HttpResponseRedirect('/ocve/editspine/' + str(s.getWork().id))


def spinesToRegionThumbs(spines, range=1):
    regions = []
    for spine in spines:
        barregions = BarRegion.objects.filter(bar=spine.bar,
                                              pageimage__page__sourcecomponent=spine.sourcecomponent).distinct()
        for r in barregions:
            rangespines = None
            if range > 1:
                extent = spine.orderno + range - 1
                rangespines = BarRegion.objects.filter(bar__barspine__orderno__range=(spine.orderno, extent),
                                                       bar__barspine__source=spine.source,
                                                       pageimage__page__sourcecomponent=spine.sourcecomponent).order_by(
                    'bar__barspine__orderno').distinct()
                #b = BarRegionThumbnail(r, r.pageimage.page, r.pageimage,rangespines)
            b = BarRegionThumbnail(r, r.pageimage.page, r.pageimage, rangespines)
            regions.append(b)
    return regions


#Show a particular spine from a work
def spine(request):
    orderno = int(request.GET['orderno'])
    prev = orderno - 1
    next = orderno + 1
    if str(request.GET['work_id']) == 'posthumous':
        #Special case for posthumous works
        spines = BarSpine.objects.filter(orderno=orderno,
                                         source__sourcecomponent__sourcecomponent_workcomponent__workcomponent__work__workcollection__id=3).distinct()
        work = None
    else:
        work = Work.objects.get(id=int(request.GET['work_id']))
        #Get relevant spines from work
        barSpines = getSpinesByWork(work, orderno, 1)
        #Arrange bar spines into groups based on source
        spines = sorted(barSpines, key=lambda sp: sp.source.orderno)
    #Get bar regions
    regions = spinesToRegionThumbs(spines)
    return render_to_response('dbmi/showspine.html',
                              {'work': work, 'orderno': orderno, 'prev': prev, 'next': next, 'regions': regions,
                               'IMAGE_SERVER_URL': settings.IMAGE_SERVER_URL},
                              context_instance=RequestContext(request))


def worksforspine(request):
    works = Work.objects.all()
    return render_to_response('dbmi/workspines.html', {'works': works},
                              context_instance=RequestContext(request))


def workspine(request, id):
    w = Work.objects.get(id=id)
    newWork = 0
    #BarSpine.objects.filter(source__sourcecomponent__sourcecomponent_workcomponent__workcomponent__work=w).delete()
    sources = Source.objects.filter(sourcecomponent__sourcecomponent_workcomponent__workcomponent__work=w).order_by(
        'orderno').distinct()
    #No spines at all for this for this work, generate
    #for s in sources:
    #if BarSpine.objects.filter(source=s).count() == 0:
    #generateSpine(s)
    return spineeditor(request, w, sources)


def spineeditor(request, work, sources):
    spines = {}
    mvtColours = ['red', 'blue', 'green', 'gold', 'brown']
    mvts = {}
    mvtIndex = {}
    cursor = connection.cursor()
    if work is not None:
        workid = str(work.id)
    else:
        workid = 'posthumous'

    sourceKeys = []
    sourceKeyString = ''

    #cursor.execute("SELECT s.id FROM ocve_source as s, ocve_sourcecomponent as sc, ocve_sourcecomponent_workcomponent as scwc, ocve_workcomponent as wc where s.id=sc.source_id and sc.id=scwc.sourcecomponent_id and scwc.workcomponent_id=wc.id and wc.work_id="+str(work.id));
    #for row in cursor.fetchall():
    for s in sources:
        sourceKeys.append(s.id)
        if len(sourceKeyString) > 0:
            sourceKeyString += ","
        sourceKeyString += str(s.id)
        spines[str(s.id)] = {}
    tbody = ''
    i = 1
    rowCounter = 1
    spineSQL = "SELECT bs.id,b.barlabel,bs.bar_id,bs.orderno,bs.source_id,bs.sourcecomponent_id,bs.implied FROM ocve_barspine as bs,ocve_bar as b where bs.bar_id=b.id and source_id in (" + sourceKeyString + ") order by source_id,bs.sourcecomponent_id,orderno;"
    cursor.execute(spineSQL)
    for row in cursor.fetchall():
        spineid = row[0]
        barlabel = row[1]
        bar_id = row[2]
        orderno = row[3]
        sourceid = row[4]
        sourcecomponentid = row[5]
        implied = row[6]
        spine = {'implied': implied, 'barlabel': barlabel, 'sourcecomponentid': sourcecomponentid}
        try:
            if mvts[sourceid] is None:
                mvts[sourceid] = sourcecomponentid
        except KeyError:
            mvts[sourceid] = sourcecomponentid
        mvtIndex[sourceid] = 0
        spines[str(sourceid)][str(orderno)] = (spine)

    while 1:
        spineFound = 0
        tbody += '<tr>\n<td><a href="/ocve/spine?work_id=' + workid + '&orderno=' + str(i) + '">' + str(
            i) + '</a></td>'
        for s in sources:
            try:
                #spine=BarSpine.objects.get(orderno=i, source=s)
                spine = spines[str(s.id)][str(i)]
                if spine['sourcecomponentid'] != mvts[s.id]:
                    mvts[s.id] = spine['sourcecomponentid']
                    mvtIndex[s.id] += 1
                    if mvtIndex[s.id] >= len(mvtColours):
                        mvtIndex[s.id] = 0
                tbody += '<td class=' + mvtColours[mvtIndex[s.id]] + '>' + spine['barlabel']
                if spine['implied'] == 1:
                    tbody += '(I)'
                tbody += '</td>'
                spineFound = 1
            except KeyError:
                tbody += '<td>&nbsp;</td>'
            except IndexError:
                tbody += '<td>&nbsp;</td>'
        tbody += '</tr>\n'
        i += 1
        if spineFound == 0:
            break
    return render_to_response('dbmi/editspine.html',
                              {'work': work, 'sources': sources, 'tbody': tbody},
                              context_instance=RequestContext(request))


#Special view for posthumous spines
def posthumousSpines(request):
    sources = Source.objects.filter(
        sourcecomponent__sourcecomponent_workcomponent__workcomponent__work__workcollection=3).order_by(
        'sourcecomponent__sourcecomponent_workcomponent__workcomponent__work').distinct()
    w = Work.objects.get(id=6397)
    return spineeditor(request, None, sources)

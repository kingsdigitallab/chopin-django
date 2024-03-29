__author__ = 'Elliot'

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from .bartools import toGeos
from ocve.forms import AnnotationForm
from ocve.models import Annotation, Annotation_BarRegion, Bar, BarRegion
from ocve.models import AnnotationType
from ocve.uiviews import ocvePageImageview
from django.shortcuts import redirect
import re

# Note edit views

# Mini wrapper class for geojson


class noteGeos:

    def __init__(self, annotation):
        self.annotation = annotation
        self.barregions = annotation.getBarRegions()
        self.geos = []

        if self.barregions.count() > 0:
            self.geos = toGeos(self.barregions, "OL3")

# Delete user annotation


@csrf_exempt
@login_required
def deleteNote(request, id):
    pageimageid = 0
    try:
        a = Annotation.objects.get(id=id)
        pageimageid = a.pageimage_id
        a.delete()
    except:
        pass

    messages.info(request, 'Annotation deleted.')
    rendered_messages = render_to_string(
        'frontend/messages.html', {'messages': messages.get_messages(request)})

    data = {
        'messages': rendered_messages
    }

    return redirect('/ocve/browse/pageview/' +
                    str(a.pageimage_id) + '/?view=annotations')


# Takes an annotation form and updates
@csrf_exempt
@login_required
def saveNote(request):
    annotation_id = request.POST['annotation_id']
    annotation = None
    if annotation_id is None or len(annotation_id) == 0:
        annotation_id = 0
    if int(annotation_id) > 0:
        # Update
        annotation = Annotation.objects.get(id=int(annotation_id))
        # Clear previous notes
        Annotation_BarRegion.objects.filter(annotation=annotation).delete()
    else:
        # Insert Annotation()
        annotation = Annotation()

    try:
        annotation_type_id = request.POST['type_id']
        annotation_type = AnnotationType.objects.get(
            id=int(annotation_type_id))
    except Exception:
        annotation_type = AnnotationType.objects.get(id=1)

    form = AnnotationForm(request.POST, instance=annotation)
    form.type = annotation_type

    new_annotation = form.save()
    new_annotation.notetext = new_annotation.notetext.strip()
    new_annotation.save()

    # Transform POLYGON feature def for later GeoJSON export
    geotext = new_annotation.noteregions
    if len(geotext) > 0:
        # geotext = geotext.replace('POLYGON((', '').replace('))', '').replace(
        #     ',', '],[').replace(' ', ',')
        # new_annotation.noteregions = '[' + geotext + ']'
        m = re.search("coordinates\"\:\[\[(\[.*\])\]\]", geotext)
        if m is not None:
            new_annotation.noteregions = m.group(1)
        new_annotation.save()

    # Recalculate which bar regions intersect with this note
    try:
        bars = request.POST['noteBars']
        labels = bars.split(',')

        for label in labels:
            bar = Bar.objects.filter(barlabel=label)
            if bar and bar.count() > 0:
                regions = BarRegion.objects.filter(
                    bar=bar, pageimage_id=new_annotation.pageimage_id)

                for region in regions:
                    Annotation_BarRegion(
                        annotation=new_annotation, barregion=region).save()
    except Exception:
        pass

    messages.info(request, 'Annotation saved.')
    rendered_messages = render_to_string(
        'frontend/messages.html', {'messages': messages.get_messages(request)})

    data = {
        'note': new_annotation,
        'messages': rendered_messages
    }

    return redirect('/ocve/browse/pageview/' +
                    str(new_annotation.pageimage_id) +
                    '/?view=annotations')


@csrf_exempt
def getAnnotations(request, id):
    notes = Annotation.objects.filter(
        annotation_barregion__barregion_id=id, type_id__gt=1)

    return render(request, 'frontend/ajax/annotations.html',
                              {'notes': notes})


@csrf_exempt
def getNoteRegions(request, id):
    return getAnnotationRegions(request, id, 1)


@csrf_exempt
def getCommentRegions(request, id):
    return getAnnotationRegions(request, id, 2)


@csrf_exempt
def getAnnotationRegions(request, id, noteType=2):
    if noteType == 1:
        # User annotations
        notes = Annotation.objects.filter(pageimage_id=id, type_id__gt=2)
    else:
        # OCVE Commentary
        notes = Annotation.objects.filter(pageimage_id=id, type_id=2)
    annotations = []

    for n in notes:
        annotations.append(noteGeos(n))

    return render(request, 'geojson.html',
                              {'annotations': annotations, 'grouped': 0})

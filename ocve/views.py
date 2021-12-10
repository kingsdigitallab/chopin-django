# Create your views here.

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render
from wagtail.core.models import Page
from wagtail.search.models import Query

from .dbmi.dbmiviews import *
from .uiviews import *

IIP_URL = settings.IIP_URL
IMAGE_SERVER_URL = settings.IMAGE_SERVER_URL

# Image format for all uploaded pages
# Forced rather than detected because only tifs should be uploaded
UPLOAD_EXTENSION = '.tif'

# Error reporting template
errorPage = 'error.html'


def uploadOCVE(request):
    # log = upload(request)
    return HttpResponse(log)


@csrf_exempt
def getBarRegions(request, id):
    geos = getGeoJSON(id, "OL3")
    return render(request,
        'geojson.html', {
            'geoRegions': geos, 'grouped': 0}
                  )


@csrf_exempt
def getOL2BarRegions(request, id):
    geos = getGeoJSON(id, "OL2")
    return render(request,
        'geojson.html', {
            'geoRegions': geos, 'grouped': 0})


def getViewInPageRegions(request, id, barid):
    geos = getViewInPageJSON(id, barid)
    return render(request,
        'geojson.html', {
            'geoRegions': geos, 'grouped': 0})


@csrf_exempt
def getGroupedBarRegions(request, id):
    geos = getGeoJSON(id, "OL2")
    return render(request,
        'geojson.html', {
            'geoRegions': geos, 'grouped': 1})


def updateSourceComponent(request):
    page_id = int(request.POST['page_id'])
    component_id = int(request.POST['sourcecomponent_id'])
    p = Page.objects.get(id=page_id)
    sc = SourceComponent.objects.get(id=component_id)
    if p is not None and sc is not None:
        p.sourcecomponent = sc
        p.save()
    return HttpResponseRedirect("/ocve/structure/18153/#" + str(page_id))


def login_page(request):
    return render(
        request,
        'registration/login-page.html',
        {},
    )


def user_profile(request):
    if request.user and request.user.id:
        annotations = Annotation.objects.filter(user_id=request.user.id)

    return render(
        request,
        "registration/user_profile.html",
        {'annotations': annotations},
    )


def _paginate(request, items):
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(items, settings.ITEMS_PER_PAGE)

    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        page = paginator.page(1)

    return page


def search(request):
    # Search
    search_query = request.GET.get('q', None)

    if search_query:
        queryset = Page.objects.live().search(search_query)

        # logs the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()
    else:
        queryset = Page.objects.none()

    search_results = _paginate(request, queryset)

    # Render template
    return render(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
    })

__author__ = 'Elliot'

from django.conf.urls import include, url
from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet

from catalogue.views import FacetedSearchView
from .annotationviews import *
from .dbmi.uploader import newsourcefiles, posth
from .views import *

# sqs = SearchQuerySet().filter(SQ(document='Source') | SQ(
# document='Opus')).filter(ocve=True).filter(live=True).order_by(
# 'orderno').facet('document')
sqs = SearchQuerySet().order_by('orderno').facet('resource').facet('document')

urlpatterns = [
    # DBMI
    url(r'^', include('ocve.dbmi.dbmi_urls')),

    # UI URLS
    url(r'^browse/barview$', barview),
    # (r'^correctsi/$', correctSourceInformation ),
    url(r'^browse/acview/(?P<acHash>[\d|\w]+)/$', acview),
    url(r'^browse/sourcejs/$', sourcejs),
    url(r'^browse/$', browse, name='ocve_browse'),
    url(r'^browse/source/(?P<id>\d+)/$',
        browse_source, name='ocve_browse_source'),
    url(r'^browse/work/(?P<id>\d+)/$',
        browse_work, name='ocve_browse_work'),
    url(r'^browse/pageview/(?P<id>\d+)/$',
        ocvePageImageview, name='ocve_pageview'),
    url(r'^browse/pageview/(?P<id>\d+)/(?P<selectedregionid>\d+)/$',
     ocvePageImageview),
    url(r'^browse/shelfmarkview/(?P<acHash>[\d|\w]+)/$',
     shelfmarkview),
    url(r'^browse/sourceinformation/(?P<id>\d+)/$',
        sourceinformation, name='ocve_sourceinformation'),
    url(r'^browse/image-preview/(?P<id>\d+)/$',
        imagePreview, name='ocve_imagepreview'),
    url(r'^browse/workinformation/(?P<id>\d+)/$',
        workinformation, name='ocve_workinformation'),
    url(r'^browse/serializeFilter/$', serializeFilter),
    url(r'^browse/resetFilter/$', resetFilter),
    # Ajax url for annotation fetch
    url(r'^browse/getAnnotations/(?P<id>\d+)/$',
     getAnnotations),

    url(r'^data/verifyImages/', verifyImages),

    url(r'^getBarRegions/(?P<id>\d+)/$', getBarRegions),
    url(r'^getOL2BarRegions/(?P<id>\d+)/$', getOL2BarRegions),
    url(r'^getBarRegions/(?P<id>\d+)/(?P<barid>\d+)/$',
     getViewInPageRegions),
    url(r'^getGroupedBarRegions/(?P<id>\d+)/$',
     getGroupedBarRegions),

    # Annotation URLS
    url(r'^saveNote/$', saveNote, name='save-note'),
    url(r'^deleteNote/(?P<id>\d+)/$',
        deleteNote, name='delete-note'),
    url(r'^newsourcefiles/$', newsourcefiles),
    url(r'^getAnnotationRegions/(?P<id>\d+)/$',
     getNoteRegions),
    url(r'^getCommentRegions/(?P<id>\d+)/$',
     getCommentRegions),
    url(r'^posth/$', posth),

    # Ajax URLS for inline collections
    url(r'^ajax/inline-collections/$', ajaxInlineCollections),
    url(r'^ajax/change-collection-name/$',
        ajaxChangeCollectionName),
    url(r'^ajax/add-collection/$', ajaxAddCollection),
    url(r'^ajax/add-image-to-collection-modal/$',
        ajaxAddImageToCollectionModal),
    url(r'^ajax/add-image-to-collection/$',
        ajaxAddImageToCollection),
    url(r'^ajax/delete-image-from-collection/$',
        ajaxDeleteImageFromCollection),
    url(r'^ajax/delete-collection/$', ajaxDeleteCollection),

    # User account management - required for OCVE UI
    url(r'^accounts/profile/$', user_profile),
    url(r'^accounts/login-page/$', login_page),
    url(r'^accounts/',
        include('registration.backends.default.urls')),
    url(r'^search/',
        FacetedSearchView(form_class=FacetedSearchForm,
                          load_all=True,
                          searchqueryset=sqs),
        name='ocve_haystack_search')
]

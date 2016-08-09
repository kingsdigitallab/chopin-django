__author__ = 'Elliot'
from django.conf.urls import patterns, include, url

from annotationviews import *
from dbmi.uploader import newsourcefiles, posth
from views import *

from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet, SQ
from catalogue.views import FacetedSearchView


sqs = SearchQuerySet().filter(SQ(document='Source') | SQ(document='Opus')).filter(ocve=True).filter(live=True).order_by('orderno').facet('document')

urlpatterns = patterns('',
                       # DBMI
                       (r'^', include('ocve.dbmi.dbmi_urls')),

                       # UI URLS
                       (r'^browse/barview$', barview),
                       #(r'^correctsi/$', correctSourceInformation ),
                       (r'^browse/acview/(?P<acHash>[\d|\w]+)/$', acview),
                       (r'^browse/sourcejs/$', sourcejs),
                       url(r'^browse/$', browse, name='ocve_browse'),
                       url(r'^browse/source/(?P<id>\d+)/$', browse_source, name='ocve_browse_source'),
                       url(r'^browse/work/(?P<id>\d+)/$', browse_work, name='ocve_browse_work'),
                       url(r'^browse/pageview/(?P<id>\d+)/$',
                           ocvePageImageview, name='ocve_pageview'),
                       (r'^browse/pageview/(?P<id>\d+)/(?P<selectedregionid>\d+)/$',
                        ocvePageImageview),
                       (r'^browse/shelfmarkview/(?P<acHash>[\d|\w]+)/$',
                        shelfmarkview),
                       url(r'^browse/sourceinformation/(?P<id>\d+)/$',
                           sourceinformation, name='ocve_sourceinformation'),
                       url(r'^browse/workinformation/(?P<id>\d+)/$',
                           workinformation, name='ocve_workinformation'),
                       (r'^browse/serializeFilter/$', serializeFilter),
                       (r'^browse/resetFilter/$', resetFilter),
                       # Ajax url for annotation fetch
                       (r'^browse/getAnnotations/(?P<id>\d+)/$',
                        getAnnotations),

                       (r'^data/verifyImages/', verifyImages),

                       (r'^getBarRegions/(?P<id>\d+)/$', getBarRegions),
                       (r'^getBarRegions/(?P<id>\d+)/(?P<barid>\d+)/$',
                        getViewInPageRegions),
                       (r'^getGroupedBarRegions/(?P<id>\d+)/$',
                        getGroupedBarRegions),

                       # Annotation URLS
                       (r'^saveNote/$', saveNote),
                       (r'^deleteNote/(?P<id>\d+)$', deleteNote),
                       (r'^newsourcefiles/$', newsourcefiles),
                       (r'^getAnnotationRegions/(?P<id>\d+)/$',
                        getAnnotationRegions),
                       (r'^posth/$', posth),

                       # Ajax URLS for inline collections
                       (r'^ajax/inline-collections/$', ajaxInlineCollections),
                       (r'^ajax/change-collection-name/$',
                        ajaxChangeCollectionName),
                       (r'^ajax/add-collection/$', ajaxAddCollection),
                       (r'^ajax/add-image-to-collection-modal/$',
                        ajaxAddImageToCollectionModal),
                       (r'^ajax/add-image-to-collection/$',
                        ajaxAddImageToCollection),
                       (r'^ajax/delete-image-from-collection/$',
                        ajaxDeleteImageFromCollection),
                       (r'^ajax/delete-collection/$', ajaxDeleteCollection),

                       # User account management - required for OCVE UI
                       (r'^accounts/profile/$', user_profile),
                       (r'^accounts/login-page/$', login_page),
                       (r'^accounts/',
                        include('registration.backends.default.urls')),
                       url(r'^search/',
                           FacetedSearchView(form_class=FacetedSearchForm,
                                             load_all=True,
                                             searchqueryset=sqs),
                           name='haystack_search')
                       )
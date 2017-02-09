__author__ = 'Elliot'
from django.conf.urls import patterns, url
from views import *

from catalogue.views import FacetedSearchView
from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet, SQ


# URLS for the CFEO skin of the UI
sqs = SearchQuerySet().filter(SQ(document='Source') | SQ(document='Opus')).filter(
    cfeo=True).filter(live=True) .order_by('orderno').facet('document')

urlpatterns = patterns('',
                       url(r'^browse/$',
                           cfeoBrowse,
                           name='cfeo_browse'),
                       url(r'^browse/image-preview/(?P<id>\d+)/$',
                           cfeoImagePreview,
                           name='cfeo_imagepreview'),
                       url(r'^browse/source/(?P<id>\d+)/$',
                           browse_source,
                           name='ocve_browse_source'),
                       url(r'^browse/work/(?P<id>\d+)/$',
                           browse_work,
                           name='ocve_browse_work'),
                       (r'^browse/acview/(?P<acHash>[\d|\w]+)/$',
                           cfeoacview),
                       url(r'^browse/pageview/(?P<id>\d+)/$',
                           cfeoPageImageview,
                           name='cfeo_pageview'),
                       url(r'^browse/comparepageview/(?P<compareleft>\d*)/(?P<compareright>\d*)/$',
                           comparePageImageview,
                           name='cfeo_comparepageview'),
                       url(r'^browse/comparepageview/(?P<compareleft>\d*)/$',
                           comparePageImageview,
                           name='cfeo_compareleftpageview'),
                       (r'^browse/comparepageview/$',
                           comparePageImageview),
                       url(r'^browse/sourceinformation/(?P<id>\d+)/$',
                           cfeoSourceInformation,
                           name='cfeo_sourceinformation'),
                       url(r'^browse/workinformation/(?P<id>\d+)/$',
                           cfeoWorkInformation,
                           name='cfeo_workinformation'),
                       url(r'^search/',
                           FacetedSearchView(form_class=FacetedSearchForm,
                                             load_all=True,
                                             searchqueryset=sqs),
                           name='cfeo_haystack_search'))

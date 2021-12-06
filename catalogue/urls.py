from django.conf.urls import url
from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet, SQ

from catalogue.views import FacetedSearchView

sqs = SearchQuerySet().exclude(
    SQ(document='Source') | SQ(document='Opus')).order_by(
    '-_score').order_by('sort_order').facet('document')

urlpatterns = [
    url(r'^search/',
        FacetedSearchView(form_class=FacetedSearchForm,
                          load_all=True,
                          searchqueryset=sqs),
        name='haystack_search'),
]

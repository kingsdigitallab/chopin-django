import os.path

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
# Signal handlers
from wagtail.search.signal_handlers import register_signal_handlers as \
    wagtailsearch_register_signal_handlers
from ocve.views import search
from ddhldap.signal_handlers import register_signal_handlers as \
    ddhldap_register_signal_handlers
from ocve.uiviews import iipredirect

wagtailsearch_register_signal_handlers()

ddhldap_register_signal_handlers()

admin.autodiscover()

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', admin.site.urls),
]

try:
    if settings.DEBUG:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/',
                include(debug_toolbar.urls)),
        ]
except ImportError:
    pass

urlpatterns += [
    url(r'^aco/', include('catalogue.urls')),
    url(r'^ocve/', include('ocve.urls')),
    url(r'^cfeo/', include('ocve.cfeourls')),
    url(r'^iip/(?P<path>.*$)', iipredirect),
    url(r'^tinymce/', include('tinymce.urls')),

    url(r'^frontend/search/', search),
    url(r'wagtail/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'', include(wagtail_urls)),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL + 'images/',
                          document_root=os.path.join(settings.MEDIA_ROOT,
                                                     'images'))

urlpatterns += static(settings.MEDIA_URL + 'documents/',
                      document_root=os.path.join(settings.MEDIA_ROOT,
                                                 'documents'))

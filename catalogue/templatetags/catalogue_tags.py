from bs4 import BeautifulSoup

from catalogue.models import Impression

from django import template
from django.utils.safestring import mark_safe

from wagtail.core.models import Page
from wagtail.core.templatetags.wagtailcore_tags import pageurl
from wagtail.documents.models import Document

from ..models import HomePage, IndexPage

import re


register = template.Library()


@register.inclusion_tag('catalogue/tags/breadcrumbs.html',
                        takes_context=True)
def breadcrumbs(context, root, current_page, extra=None):
    """Returns the pages that are part of the breadcrumb trail of the current
    page, up to the root page."""
    print("breadcrumb {}\n".format(current_page))
    pages = IndexPage.objects.none()
    try:
        pages = current_page.get_ancestors(
            inclusive=True).descendant_of(root).filter(live=True)
    except AttributeError:
        current_page = Page.objects.filter(slug=current_page).first()
        pages = current_page.get_ancestors(
            inclusive=True).descendant_of(root).filter(live=True)
        root = get_site_root(context)


    return {'request': context['request'], 'root': root,
            'current_page': current_page, 'pages': pages, 'extra': extra}

@register.simple_tag(takes_context=True)
def catalogueurl(context, page, *args):
    """Returns the URL for the page that has the given slug."""
    return pageurl(context, page) + '/'.join([str(arg) for arg in args]) + '/'

@register.filter
def clean(text):
    return text

@register.filter
def get_item(dictionary, key):
    return dictionary[key]

@register.simple_tag(takes_context=True)
def get_site_root(context):
    """Returns the site root Page, not the implementation-specific model used.

    :rtype: `wagtail.core.models.Page`
    """
    if 'BASE_URL' in context:
        return Page.objects.filter(slug=context['BASE_URL']).first()
    else:
        return context['request'].site.root_page

@register.filter
def is_current_or_ancestor(page, current_page):
    """Returns True if the given page is the current page or is an ancestor of
    the current page."""
    return current_page.is_current_or_ancestor(page)

@register.inclusion_tag('catalogue/tags/local_menu.html', takes_context=True)
def local_menu(context, current_page=None):
    """Retrieves the secondary links for the 'also in this section' links -
    either the children or siblings of the current page."""
    menu_pages = []
    label = current_page.title

    if current_page:
        menu_pages = current_page.get_children().filter(
            live=True, show_in_menus=True)

        # if no children, get siblings instead
        if len(menu_pages) == 0:
            menu_pages = current_page.get_siblings().filter(
                live=True, show_in_menus=True)

        if current_page.get_children_count() == 0:
            if not isinstance(current_page.get_parent().specific, HomePage):
                label = current_page.get_parent().title

    # required by the pageurl tag that we want to use within this template
    return {'request': context['request'], 'current_page': current_page,
            'menu_pages': menu_pages, 'menu_label': label}


@register.inclusion_tag('catalogue/tags/main_menu.html', takes_context=True)
def main_menu(context, root, current_page=None):
    """Returns the main menu items, the children of the root page. Only live
    pages that have the show_in_menus setting on are returned."""
    menu_pages = root.get_children().filter(live=True, show_in_menus=True)

    return {'request': context['request'], 'root': root, 'BASE_URL':context['BASE_URL'],
            'current_page': current_page, 'menu_pages': menu_pages}

@register.filter
def order_by(queryset, order):
    return queryset.order_by(order)

@register.filter
def pdfdisplay(html):
    """Returns `html` with links to PDF Documents replaced with the
    display of those documents.

    Since there are templates for displaying PDFs that are used in
    other contexts, reuse them here by constructing a template string
    that includes them and rendering it.

    """
    soup = BeautifulSoup('<div>{}</div>'.format(html))
    links = soup(linktype='document')
    keys = []

    for link in links:
        key = link.get('id')

        if key:
            try:
                document = Document.objects.get(id=key)
            except:
                continue

            canvas_id = 'pdf_{}'.format(key)
            pdf_url = document.file.url
            canvas = '{{% include "catalogue/includes/pdf_display.html" with canvas_id="{}" pdf_url="{}" %}}'.format(canvas_id, pdf_url)
            link.parent.replace_with(canvas)
            keys.append((canvas_id, pdf_url))

    for canvas_id, pdf_url in keys:
        script_include = '{{% include "catalogue/includes/pdf_script.html" with canvas_id="{}" pdf_url="{}" %}}'.format(canvas_id, pdf_url)
        soup.div.append(script_include)

    html = str(soup.div)
    html = re.sub(r'><\/embed>', ' />', html)

    return template.Template(html).render(template.Context())

@register.filter
def add_special_characters(html):
    #html = html.encode('utf-8')

    patterns = {
        'start_tag': r'(?P<start_tag><[^>]*>)',
        'end_tag': r'(?P<end_tag></[^>]*>)',
        'code': r'(?P<code>.*?)',
        'class': r'(?P<class>[\w-]+)',
    }

    code_pattern = r'\[\[{class}\]{start_tag}?{code}{end_tag}?\]'.format(
        **patterns)

    if not re.search(code_pattern, html):
        return html

    return mark_safe(re.sub(code_pattern, _format_code, html))

def _format_code(match):
    try:
        code_as_class = match.group('code')
        code = chr(int(code_as_class))
    except ValueError:
        code_as_class = match.group('code') or ''
        code = code_as_class

    parts = {
        'start_tag': match.group('start_tag') or '',
        'end_tag': match.group('end_tag') or '',
        'code_as_class': code_as_class,
        'code': code,
        'class': match.group('class').lower(),
    }

    repl = '<span class="{class} c{code_as_class}">{start_tag}{code}{end_tag}</span>'.format(
        **parts)

    return repl #.encode('utf-8')

@register.filter
def truncate_comments(value):
    truncated = value
    suffix = '.'

    index = value.find('.')
    index_char2 = value.find('%')

    if index_char2 > index:
        index = index_char2
        suffix = ''

    if index > 0:
        truncated = value[:index] + suffix

    return truncated

@register.simple_tag()
def get_impression_exists(code_hash):
    """Returns true if the impression with the give ac code hash exists in the
    ACO Online."""
    impressions = Impression.objects.filter(code_hash=code_hash)

    return len(impressions) > 0

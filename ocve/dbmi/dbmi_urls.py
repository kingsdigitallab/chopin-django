__author__ = 'Elliot'

from django.conf.urls import url

from ocve.views import *
from .bareditor import *
from .sourceeditor import *
from .spine import *
from .uploader import convertFolder, convertimage

urlpatterns = [
    # Source and source information
    url(r'^sources/$', sources),  # New source view
    url(r'^sourceviews/(?P<m>\d+)/$', sourceView),
    url(r'^sourceview/(?P<id>\d+)/$', uncorrectedSource),
    url(r'^sourceeditor/(?P<id>\d+)/$', existingsourceeditor),
    url(r'^sourceeditor/new/(?P<id>\d+)/$', newsourceeditor),
    url(r'^sourceeditor/$', sourceeditor),
    url(r'^saveSource/(?P<id>\d+)/$', saveSource),
    url(r'^saveSourceInformation/(?P<id>\d+)/$',
     saveSourceInformation),
    url(r'^clonesource/(?P<id>\d+)/$', clonesource),
    url(r'^clonepage/(?P<id>\d+)/$', clonepage),
    url(r'^generatesourcethumbnails/(?P<id>\d+)/$',
     generateSourceThumbnails),

    # Source/work components
    # url(r'^sourcecomp/(?P<id>\d+)/$', sourceComp),
    url(r'^editsourcecomponent/(?P<id>\d+)/$',
     editexistingsourcecomponent),
    url(r'^deletesourcecomponent/(?P<id>\d+)/$',
     deletesourcecomponent),
    url(r'^savesourcecomponent/(?P<id>\d+)/$', savesourcecomponent),
    url(r'^updatecomponentorder/$', updateComponentOrder),
    url(r'^createsourcecomponent/(?P<sourceid>\d+)/$',
     createsourcecomponent),
    url(r'^createfrontmatter/(?P<sourceid>\d+)/$', createfrontmatter),
    url(r'^createendmatter/(?P<sourceid>\d+)/$', createendmatter),
    url(r'^updatesc/$', updateSourceComponent),
    url(r'^deletesource/(?P<id>\d+)/$', deletesource),

    # Pages and bars
    url(r'^page/(?P<id>\d+)/$', loadEditPage),
    url(r'^correctCropping/', correctCrop),
    url(r'^editbars/(?P<id>\d+)/$',
        editBars, name="edit-bars"),
    url(r'^cropCorrect/(?P<id>\d+)/$', cropCorrectView),
    url(r'^reorderBars/$', reorderBarNumbers),
    url(r'^deletepage/(?P<id>\d+)/$', deletepage),
    url(r'^savePage/$', savePage),
    url(r'^updatePageIndex/$', updatepageindex),
    url(r'^defaultpageorder/(?P<id>\d+)/$', defaultpageorder),
    url(r'^updatepagetype/(?P<id>\d+)/$', updatepagetype),
    url(r'^updatecopyright/$', updatecopyright),

    # Misc

    url(r'^fixbarrange/$', findmeta),
    # url(r'^structure/(?P<id>\d+)/$', sourceStructureView),
    url(r'^updateStatus/$', updateStatus),
    url(r'^dbmi/$', dbmiView),
    url(r'^findunverified/$', findUnverifiedImages),
    url(r'^sourcesbywork/$', sourcesbywork),
    url(r'^generatethumbnails/$', generateAllThumbnails),
    url(r'^pushtoliv/$', pushtoliv),

    # upload
    url(r'^upload/selectsource/', selectSource),
    url(r'^upload/addsource/', addSource),
    url(r'^upload/addpage/', addPages),
    url(r'^upload/page/(?P<id>\d+)/$', iipPage),
    url(r'^upload/addtosource/(?P<id>\d+)/$', addToSource),
    url(r'^upload/modifypage/$', modifyPage),
    url(r'^updateBarRegions/$', updateBarRegion),
    url(r'^updateBarNumber/$', updateBarNumber),
    url(r'^convertfolder/(?P<folderName>.*)/$', convertFolder),
    url(r'^convertimage/$', convertimage),

    # Spine URLS
    # List of works
    url(r'^spines/$', worksforspine),
    # Spines for a single work
    url(r'^editspine/(?P<id>\d+)/$', workspine),
    url(r'^posthumousspine/$', posthumousSpines),
    # A single part of a spine
    url(r'^spine$', spine),
    url(r'^importspine/$', importXLS),
    # Export/import in CSV for editing
    url(r'^exportspine/(?P<id>\d+)/$', exportXLS),
    url(r'^deletesourcespines/(?P<id>\d+)/$', deleteSourceSpines),
    # url(r'^work/(?P<id>\d+)/$', work),
    url(r'^workadmin/(?P<id>\d+)/$', workadmin),
    url(r'^savework/(?P<id>\d+)/$', savework),
    url(r'^saveworkinformation/(?P<id>\d+)/$', saveworkinformation),
    url(r'^saveworkcomponents/(?P<id>\d+)/$', saveworkcomponents),
    url(r'^works/', works),

]

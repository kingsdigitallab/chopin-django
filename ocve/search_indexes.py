__author__ = 'elliotthall'
from django.contrib.contenttypes.models import ContentType
from haystack import indexes
from models import WorkInformation,Work,SourceInformation,Source,Genre

class WorkIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    document = indexes.FacetCharField(default='Opus')
    label = indexes.CharField(model_attr="label")
    genres = indexes.MultiValueField()
    orderno = indexes.IntegerField(model_attr="orderno")
    url = indexes.CharField(indexed=False, null=True)
    title = indexes.CharField()

    def prepare_title(self, obj):
        return obj.label

    def prepare_url(self,obj):
        mode="ocve"
        #if obj.ocve == True:
        #    mode="OCVE"
        return "/"+mode+"/browse/work/"+str(obj.id)+"/"

    def get_model(self):
        return Work

    def prepare_genres(self,obj):
        return [g.genre for g in Genre.objects.filter(work__id=obj.id).distinct()]

    def index_queryset(self, using=None):
        return self.get_model().objects.filter().order_by('orderno')



class SourceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    document = indexes.FacetCharField(default='Source')
    #work = indexes.CharField(model_attr="getWork__label")
    #accode =
    #instruments = indexes.MultiValueField(model_attr="getInstruments")
    sourcetype = indexes.CharField(model_attr="sourcetype__type")
    ocve=indexes.BooleanField(default=False,model_attr="ocve")
    cfeo=indexes.BooleanField(default=False,model_attr="cfeo")
    live=indexes.BooleanField(default=False,model_attr="live")
    orderno = indexes.IntegerField(model_attr="orderno")
    url = indexes.CharField(indexed=False, null=True)
    title = indexes.CharField()

    def prepare_title(self, obj):
        if obj.ocve == True:
            return obj.getOpusLabel()
        else:
            return obj.cfeolabel

    def prepare_url(self,obj):
        mode="cfeo"
        if obj.ocve == True:
            mode="ocve"
        return "/"+mode+"/browse/source/"+str(obj.id)+"/"

    def get_model(self):
        return Source

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(live=True).order_by('orderno')
__author__ = 'Elliott Hall'

from haystack import indexes

from models import Work, Source, Genre


class WorkIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    document = indexes.FacetCharField(default='Opus')
    label = indexes.CharField(model_attr="label")
    genres = indexes.MultiValueField()
    orderno = indexes.IntegerField(model_attr="orderno")
    url = indexes.CharField(indexed=False, null=True)
    ocve = indexes.BooleanField()
    cfeo = indexes.BooleanField()
    live = indexes.BooleanField()
    resource = indexes.FacetMultiValueField()
    title = indexes.CharField()

    def prepare_title(self, obj):
        return obj.label

    def prepare_cfeo(self, obj):
        return Work.objects.filter(
            id=obj.id,
            workcomponent__sourcecomponent_workcomponent__sourcecomponent__source__cfeo=True).exists()

    def prepare_ocve(self, obj):
        return Work.objects.filter(
            id=obj.id,
            workcomponent__sourcecomponent_workcomponent__sourcecomponent__source__ocve=True).exists()

    def prepare_live(self, obj):
        return Work.objects.filter(
            id=obj.id,
            workcomponent__sourcecomponent_workcomponent__sourcecomponent__source__live=True).exists()

    def prepare_resource(self, obj):
        resources = []
        if self.ocve:
            resources.append("OCVE")
        if self.cfeo:
            resources.append("CFEO")
        return resources

    def prepare_url(self, obj):
        return "/browse/work/" + str(obj.id) + "/"

    def get_model(self):
        return Work

    def prepare_genres(self, obj):
        return [
            g.genre for g in Genre.objects.filter(
                work__id=obj.id).distinct()]

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            workcomponent__sourcecomponent_workcomponent__sourcecomponent__source__live=True).order_by('orderno')


class SourceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    document = indexes.FacetCharField(default='Source')
    sourcetype = indexes.CharField(model_attr="sourcetype__type")
    ocve = indexes.BooleanField(default=False, model_attr="ocve")
    cfeo = indexes.BooleanField(default=False, model_attr="cfeo")
    live = indexes.BooleanField(default=False, model_attr="live")
    resource = indexes.FacetMultiValueField()
    orderno = indexes.IntegerField(model_attr="orderno")
    url = indexes.CharField(indexed=False, null=True)
    title = indexes.CharField()

    def prepare_title(self, obj):
        if obj.ocve:
            return obj.getOpusLabel()
        else:
            return obj.cfeolabel

    def prepare_url(self, obj):
        return "/browse/source/" + str(obj.id) + "/"

    def get_model(self):
        return Source

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(live=True).order_by('orderno')

    def prepare_resource(self, obj):
        resources = []
        if obj.ocve:
            resources.append("OCVE")
        if obj.cfeo:
            resources.append("CFEO")
        return resources

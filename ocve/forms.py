__author__ = 'Elliot'
from django.forms import HiddenInput,ModelForm,Select,modelformset_factory
from django import forms
from models import *
from tinymce.widgets import TinyMCE

class WorkForm(ModelForm):

    class Meta:
        model = Work
        exclude = ('workinformation',)

class NewSourceForm(ModelForm):
     class Meta:
         model = NewSource
         exclude = ('sourcecreated',)

class SourceForm(ModelForm):

    class Meta:
        model = Source
        exclude = ('',)

class SourceComponentForm(ModelForm):
    class Meta:
        model = SourceComponent
        exclude = ('overridelabel',)

class WorkInformationForm(ModelForm):

    class Meta:
        model = WorkInformation
        exclude = ('',)

class WorkComponentForm(ModelForm):

    class Meta:
        model = WorkComponent
        exclude = ('',)

WorkComponentFormset=modelformset_factory(WorkComponent,exclude=())

class SourceInformationForm(ModelForm):

    class Meta:
        model = SourceInformation
        exclude = ('',)

class AnnotationForm(ModelForm):

    def __init__(self,*args,**kwargs):
        super (AnnotationForm,self ).__init__(*args,**kwargs) # populates the post
        self.fields['type'].queryset = AnnotationType.objects.filter(id__gt=2)


    class Meta:
        model = Annotation
        fields = ['id','notetext','noteregions','pageimage','user','type']
        widgets = { 'id':HiddenInput(),
                    'user':HiddenInput(),
                    'pageimage':HiddenInput(),
                    'noteregions':HiddenInput(),
                    'geometry':HiddenInput(),
                    'type':Select(choices=( ('3','Private'),('4','Public') ))
        }



__author__ = 'elliotthall'
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from ocve.models import *

#Populate the meieditor for editing
    #Non-prototype will have extra navigation objects
def meieditor(request,id=65054):
    pi=PageImage.objects.get(id=id)
    return render_to_response('dbmi/meieditor.html', {'pi': pi}, context_instance=RequestContext(request))

def savemei(request,id):
    try:
        mei=request.POST['mei']
        pi=PageImage.objects.get(id=id)
        pi.mei=mei
        pi.save()
    except Exception, e:
        print e
    return meieditor(request,id)
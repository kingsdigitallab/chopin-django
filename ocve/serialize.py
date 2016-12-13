__author__ = 'elliotthall'
#Helper methods to serialize the distributed source db structures, primarily to make fixtures for testing
from django.core import serializers

from ocve.models import *


def serializeAuthorityLists():
    pass

#Serialize a work, its components and opus no
#6337
def serializeWork(works):
    data=''
    if works is not None and works.count() > 0:
        jsonserializer=serializers.get_serializer("json")
        jsons=jsonserializer()
        jsons.serialize(works)
        data=jsons.getvalue()
        wcs=WorkComponent.objects.filter(work__in=works)
        jsons.serialize(wcs)
        data+=jsons.getvalue()
    return data

#Serialize:
    # Source
    #     Components and intersections with works
def serializeSource(sources):
    #First get their works
    works=Work.objects.filter(workcomponent__sourcecomponent_workcomponent__sourcecomponent__source__in=sources).distinct()
    data=serializeWork(works)
        #Serialize
    #Serialize sources themselves
        #Intersections with work
    #sourcecomponents
    #page
    #bar
    #barregion
    pass




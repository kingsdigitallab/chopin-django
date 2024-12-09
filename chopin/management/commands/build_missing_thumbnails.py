#Rebuild the Json data for the web front end
__author__ = 'elliotthall'
from django.core.management.base import BaseCommand
from django.conf import settings
import logging
import subprocess
from optparse import make_option
from ocve.uitools import generateThumbnail
from ocve.models import PageImage
from django.db.models import Q
import os
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = """Look for missing thumbnails and add them.  DOES NOT REWRITE EXISTING THUMBNAILS"""

    def handle(self, *args, **options):
        #Get all pageimages that are to be shown (in stg or live)
        pages=PageImage.objects.filter(Q(page__sourcecomponent__source__ocve=1) | Q(page__sourcecomponent__source__cfeo=1))
        pages=pages.filter(page__sourcecomponent__source__live=True)
        #Check for file
        x=0
        for pageimage in pages:
            fname = os.path.join(settings.THUMBNAIL_DIR, str(pageimage.id) + ".jpg")
            if not os.path.isfile(fname):
                #Missing, write
                #log.info('Writing thumbnail '+fname)
                time.sleep(3)
                print(('Writing thumbnail '+fname))
                x+=1
                generateThumbnail(pageimage)
        print(('Total:'+str(x)))

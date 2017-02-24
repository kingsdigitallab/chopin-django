import math

from ocve.models import PageImage, BarRegion

__author__ = 'elliotthall'
from django.core.management.base import BaseCommand, NoArgsCommand
import logging
import subprocess
from optparse import make_option

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Adjsut bar regions for reconverted image <pageimage_id> width height"""

    # def add_arguments(self, parser):
    #     parser.add_argument('pageimage_id', type=int)
    #     parser.add_argument('width', type=int)
    #     parser.add_argument('height', type=int)

    def handle(self, *args, **options):
        pi = PageImage.objects.get(id=int(args[0]))
        barregions = BarRegion.objects.filter(pageimage=pi)
        waspect = int(args[1]) / float(pi.width)
        haspect = int(args[2]) / float(pi.height)
        self.stdout.write("width: " + str(pi.width))
        self.stdout.write("height: " + str(pi.height))
        self.stdout.write("waspect: "+str(waspect))
        self.stdout.write("haspect: " + str(haspect))
        for br in barregions:
            self.stdout.write("Source Region " + str(br.id) + ": " + str(br.x) + "," + str(br.y) + "," + str(
                br.width) + "," + str(br.height) + ",")
            br.x = math.ceil(br.x * waspect)
            br.y = math.ceil(br.y * haspect)
            br.width = math.ceil(br.width * waspect)
            br.height = math.ceil(br.height * haspect)
            self.stdout.write(
                "Changed Region " + str(br.id) + ": " + str(br.x) + "," + str(br.y) + "," + str(br.width) + "," + str(
                    br.height) + ",")
            # br.save()

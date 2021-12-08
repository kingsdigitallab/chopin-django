#Rebuild the Json data for the web front end
__author__ = 'elliotthall'
from django.core.management.base import BaseCommand
import logging
import subprocess
from optparse import make_option
from ocve.uitools import serializeOCVESourceJson,serializeCFEOSourceJson,serializeAcCodeConnector

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = """Rebuild website JSON"""

    def handle(self, *args, **options):
        logger.info('rebuild OCVE JSON')
        serializeOCVESourceJson()
        # logger.info('rebuild CFEO JSON')
        # serializeCFEOSourceJson()
        # logger.info('rebuild AC JSON')
        # serializeAcCodeConnector()


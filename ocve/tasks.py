from __future__ import absolute_import

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command
from ocve.uiviews import serializeOCVESourceJson,serializeCFEOSourceJson,serializeAcCodeConnector
logger = get_task_logger(__name__)




@shared_task
def push_to_liv():
    logger.info('Push ocve_* data from app_ocve_merged_stg to liv')
    result = call_command('pushtoliv', interactive=False)
    # if the commands succeeds it returns None
    if not result:
        logger.info('Finished update.  Rebuilding JSONs.')
        serializeOCVESourceJson()
        serializeCFEOSourceJson()
        serializeAcCodeConnector()
        logger.info('JSON rebuild complete.')
    else:
        logger.error('Failed update index: {}'.format(result.info))

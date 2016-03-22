from __future__ import absolute_import

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command

logger = get_task_logger(__name__)


@shared_task
def haystack_update_index():
    logger.info('Starting update index')
    result = call_command('update_index', interactive=False)
    logger.info('Finishing update index: {}'.format(result))

    return result

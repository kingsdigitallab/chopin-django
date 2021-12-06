

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command

logger = get_task_logger(__name__)


@shared_task
def haystack_update_index():
    logger.info('Starting update index')

    result = call_command('update_index', interactive=False)

    # if the commands succeeds it returns None
    if not result:
        logger.info('Finishing update index')
    else:
        logger.error('Failed update index: {}'.format(result.info))

    return result

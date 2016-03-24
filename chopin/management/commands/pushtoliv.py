__author__ = 'elliotthall'
from django.core.management.base import BaseCommand, NoArgsCommand
import logging
import subprocess
from optparse import make_option
import os
from ocve.scripts.updateliv import updateliv

logging.basicConfig(format='%(asctime)-15s %(message)s')
logger = logging.getLogger('Main logger')


class Command(BaseCommand):
    help = """Dumps data from stg and pushes to live, along with static JSON.  NOTE: Works only on VM"""

    option_list = BaseCommand.option_list + (
        make_option('--revert',
                    action='store_true',
                    dest='revert',
                    default=False,
                    help='Restore from last liv dump'),
    )


    def handle(self, *args, **options):
        revert = 0
        if options['revert']:
            revert = 1
        updateliv(revert)



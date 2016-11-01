__author__ = 'elliotthall'
from django.core.management.base import BaseCommand, NoArgsCommand
import logging
import subprocess
from optparse import make_option

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Dumps data from stg and pushes to live, along with static JSON.  NOTE: Works only on VM"""

    option_list = BaseCommand.option_list + (
        make_option('--revert',
                    action='store_true',
                    dest='revert',
                    default=False,
                    help='Restore from last liv dump'),
    )


    def cpscript(self, script, source, dest):
        cpcmd = ['cp', source + script, dest + script]
        subprocess.Popen(cpcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def handle(self, *args, **options):
        liv_db = 'chopin'
        stg_dump = '/vol/ocve3/dumps/pg_stg_dump.sql'
        live_dump = '/vol/ocve3/dumps/pg_liv_dump.sql'
        if options['revert']:
            #Revert scripts
            revertstat = ['psql', '-h', 'db-pg-1.cch.kcl.ac.uk', '-U', 'app_ocv', 'app_ocve_merged', '<', live_dump]
            proc = subprocess.Popen(revertstat, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            err = proc.communicate()[1]
            if err:
                print err
                logger.error('Dump from stg failed with error:' + str(err))
                return False
            else:
                logger.info('stg dump generated')

        else:

            #todo Postgres pg_dump -h db-pg-1.cch.kcl.ac.uk -U app_ocve -t 'ocve_*' app_ocve_merged_stg > ocve_only.sql
            stgdumpcmd = ['pg_dump','-w','-c','-O', '-h', 'db-pg-1.cch.kcl.ac.uk', '-U', 'app_ocve', '-t', 'ocve_*',  'app_ocve_merged_stg', '>', stg_dump]
            #' '.join(pushstat)
            proc = subprocess.Popen(' '.join(stgdumpcmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            err = proc.communicate()[1]
            if err:
                logger.error('Dump from stg failed with error:' + str(err))
                return False
            else:
                logger.info('stg dumps generated')
                #backup live
                psqllivdumpcmd = ['pg_dump','-w','-c','-O', '-h', 'db-pg-1.cch.kcl.ac.uk', '-U', 'app_ocve', '-t', 'ocve_*',  'app_ocve_merged',  '>', live_dump]
                #' '.join(pushstat)
                proc = subprocess.Popen(' '.join(psqllivdumpcmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
                err = proc.communicate()[1]
                if err:
                    logger.error('Dump from liv failed with error:' + str(err))
                    return False
                else:
                    #Push stg mysql to live
                    pushstat = ['psql', '-w','-h', 'db-pg-1.cch.kcl.ac.uk', '-U', 'app_ocve', 'app_ocve_merged',  '<', stg_dump]
                    proc = subprocess.Popen(' '.join(pushstat), stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
                    err = proc.communicate()[1]
                    if err:
                        logger.error('Push to live failed with error:' + str(err))
                        return False
                    else:
                        logger.info('stg data pushed to live')
                        #TODO add touch?

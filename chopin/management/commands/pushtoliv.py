__author__ = 'elliotthall'
from django.core.management.base import BaseCommand, NoArgsCommand
import logging
import subprocess
from optparse import make_option

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


    def cpscript(self, script, source, dest):
        cpcmd = ['cp', source + script, dest + script]
        subprocess.Popen(cpcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def handle(self, *args, **options):
        stg_db = 'ocve2real'
        liv_db = 'chopin'

        if options['revert']:
            #Revert scripts

            revertstat = ['mysql', '-u', 'root', liv_db, '<', ' /vol/ocve3/dumps/liv_dump.sql']
            proc = subprocess.Popen(revertstat, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            err = proc.communicate()[1]
            if err:
                print err
                logger.error('Dump from stg failed with error:' + str(err))
                return False
            else:
                logger.info('stg dump generated')

        else:
            #todo Postgres pg_dump -h db-pg-1.cch.kcl.ac.uk -U ehall -t 'ocve_*' app_ocve_merged_test > ocve_only.sql
            mysqlstgdumpcmd = ['pg_dump', '-h', 'db-pg-1.cch.kcl.ac.uk', '-U', 'ehall', '-t', 'ocve_*',  'app_ocve_merged_test', '>', '/vol/ocve3/dumps/pg_stg_dump.sql']
            #' '.join(pushstat)
            proc = subprocess.Popen(' '.join(mysqlstgdumpcmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            err = proc.communicate()[1]
            if err:
                logger.error('Dump from stg failed with error:' + str(err))
                return False
            else:
                logger.info('stg dumps generated')
                #backup live
                psqllivdumpcmd = ['pg_dump', '-h', 'db-pg-1.cch.kcl.ac.uk', '-U', 'ehall', '-t', 'ocve_*',  'app_ocve_merged',  '>', '/vol/ocve3/dumps/stg_dump.sql']
                #' '.join(pushstat)
                proc = subprocess.Popen(' '.join(psqllivdumpcmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
                err = proc.communicate()[1]
                if err:
                    logger.error('Dump from liv failed with error:' + str(err))
                    return False
                else:
                    #Push stg mysql to live
                    pushstat = ['psql', '-h', 'db-pg-1.cch.kcl.ac.uk', '-U', 'ehall', '-t', 'app_ocve_merged',  '<', '/vol/ocve3/dumps/stg_dump.sql']
                    proc = subprocess.Popen(' '.join(pushstat), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    err = proc.communicate()[1]
                    if err:
                        logger.error('Push to live failed with error:' + str(err))
                        return False
                    else:
                        logger.info('stg data pushed to live')
                        #TODO add touch?
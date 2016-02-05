__author__ = 'elliotthall'
from django.core.management.base import BaseCommand,NoArgsCommand
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


    def cpscript(self,script,source,dest):
        cpcmd=['cp',source+script,dest+script]
        subprocess.Popen(cpcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def handle(self, *args, **options):
        stg_db='ocve2real'
        liv_db='chopin_liv'
        stg_scripts='/vol/ocve3/webroot/stg/django/chopin/static/javascripts/'
        liv_scripts='/vol/ocve3/webroot/liv/django/chopin/static/javascripts/'
        dump_scripts='/vol/ocve3/dumps/javascript/'
        #' | ','mysql','-u root',liv_db,' < ',' mydb2' shell=True
        if options['revert']:
            #Revert scripts
            self.cpscript('OCVEsourceJSON.js',dump_scripts,liv_scripts)
            self.cpscript('CFEOsourceJSON.js',dump_scripts,liv_scripts)
            revertstat = ['mysql','-u','root',liv_db,'<',' /vol/ocve3/dumps/liv_dump.sql']
            proc = subprocess.Popen(revertstat, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            err = proc.communicate()[1]
            if err:
                logger.error('Dump from stg failed with error:'+str(err))
                return False
            else:
                logger.info('stg dump generated')

        else:
            pushstat = ['mysqldump','-u','root',stg_db,'>','/vol/ocve3/dumps/stg_dump.sql']
            proc = subprocess.Popen(pushstat, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
            err = proc.communicate()[1]
            if err:
                logger.error('Dump from stg failed with error:'+str(err))
                return False
            else:
                logger.info('stg dump generated')
                #backup live
                pushstat = ['mysqldump','-u','root',liv_db,'>','/vol/ocve3/dumps/liv_dump.sql']
                proc = subprocess.Popen(pushstat, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
                err = proc.communicate()[1]
                if err:
                    logger.error('Dump from liv failed with error:'+str(err))
                    return False
                else:
                    #Backup live JSON
                    self.cpscript('OCVEsourceJSON.js',liv_scripts,dump_scripts)
                    self.cpscript('CFEOsourceJSON.js',liv_scripts,dump_scripts)
                    #Copy rebuilt stg JSON to live.
                    self.cpscript('OCVEsourceJSON.js',stg_scripts,liv_scripts)
                    self.cpscript('CFEOsourceJSON.js',stg_scripts,liv_scripts)
                    #Push stg mysql to
                    # pushstat = ['mysqldump','-u root',stg_db,'>',' /vol/ocve3/dumps/stg_dump.sql']
                    # proc = subprocess.Popen(pushstat, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # err = proc.communicate()[1]
                    # if err:
                    #     logger.error('Push to live failed with error:'+str(err))
                    #     return False
                    # else:
                    #     logger.info('stg data pushed to live')
                    #TODO add touch?



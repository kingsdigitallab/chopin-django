#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import sys
from functools import wraps
from getpass import getuser
from socket import gethostname

from django.conf import settings
from fabric.api import cd, env, local, prefix, quiet, require, run, sudo, task
from fabric.colors import green, red, yellow
from fabric.contrib import django

# put project directory in path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)

django.project('chopin')

REPOSITORY = 'https://scm.cch.kcl.ac.uk/hg/chopin-django'

env.user = settings.FABRIC_USER
env.hosts = ['ocve3.dighum.kcl.ac.uk']
env.gateway = 'ssh.cch.kcl.ac.uk'
env.root_path = '/vol/ocve3/webroot/'
env.envs_path = os.path.join(env.root_path, 'envs')


def server(func):
    """Wraps functions that set environment variables for servers"""
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            env.servers.append(func)
        except AttributeError:
            env.servers = [func]

        return func(*args, **kwargs)
    return decorated


@task
@server
def dev():
    env.srvr = 'dev'
    set_srvr_vars()


@task
@server
def stg():
    env.srvr = 'stg'
    set_srvr_vars()


@task
@server
def liv():
    env.srvr = 'liv'
    set_srvr_vars()


@task
@server
def localhost():
    """ local server """
    env.srvr = 'local'
    env.path = os.path.dirname(os.path.realpath(__file__))
    env.within_virtualenv = 'workon chopin'
    env.hosts = [gethostname()]
    env.user = getuser()


@task
@server
def vagrant():
    env.srvr = 'vagrant'
    env.path = os.path.join('/', env.srvr)

    # this is necessary because ssh will fail when known hosts keys vary
    # every time vagrant is destroyed, a new key will be generated
    env.disable_known_hosts = True

    env.within_virtualenv = 'source {}'.format(
        os.path.join('~', 'venv', 'bin', 'activate'))

    result = dict(line.split()
                  for line in local('vagrant ssh-config',
                                    capture=True).splitlines())

    env.hosts = ['%s:%s' % (result['HostName'], result['Port'])]
    env.key_filename = result['IdentityFile']
    env.user = result['User']

    print((env.key_filename, env.hosts, env.user))


@task
def unlock():
    """os x servers need to be unlocked"""
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)
    with cd(env.path):
        run('security unlock-keychain')


def set_srvr_vars():
    env.path = os.path.join(env.root_path, env.srvr, 'django', 'chopin')
    env.within_virtualenv = 'source {}'.format(
        os.path.join(env.envs_path, 'chopin_' + env.srvr, 'bin', 'activate'))


@task
def create_virtualenv():
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)
    with quiet():
        env_vpath = os.path.join(env.envs_path, 'chopin_' + env.srvr)
        if run('ls {}'.format(env_vpath)).succeeded:
            print((
                green('virtual environment at [{}] exists'.format(env_vpath))))
            return

    print((yellow('setting up virtual environment in [{}]'.format(env_vpath))))
    run('virtualenv {}'.format(env_vpath))


@task
def clone_repo():
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)
    with quiet():
        if run('ls {}'.format(os.path.join(env.path, '.hg'))).succeeded:
            print((green(('repository at'
                         ' [{}] exists').format(env.path))))
            return

    print((yellow('cloning repository to [{}]'.format(env.path))))
    run('hg clone {} {}'.format(REPOSITORY, env.path))


@task
def setup_environment():
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)
    create_virtualenv()
    clone_repo()
    install_requirements()


@task
def deploy(branch=None):
    update(branch)
    install_requirements()
    migrate()
    own_django_log()
    collect_static()
    update_index()

    try:
        add_supervisor_conf()
    except:
        print((yellow('adding supervisor configuration may have failed')))
        print((yellow('check the server')))
        print((red(sys.exec_info())))

    touch_wsgi()


@task
def update(branch=None):
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    if branch:
        # try specified branch first
        to_branch = branch
    elif not branch and env.srvr in ['local', 'vagrant', 'dev']:
        # if loval, vagrant or dev deploy to master
        to_branch = 'default'
    else:
        # else deploy to server tag
        to_branch = env.srvr

    with cd(env.path), prefix(env.within_virtualenv):
        run('hg pull')
        run('hg up {}'.format(to_branch))


@task
def makemigrations(app=None):
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    if env.srvr in ['dev', 'stg', 'liv']:
        print((yellow('Do not run makemigrations on the servers')))
        return

    with cd(env.path), prefix(env.within_virtualenv):
        run('./manage.py makemigrations {}'.format(app if app else ''))


@task
def migrate(app=None):
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    with cd(env.path), prefix(env.within_virtualenv):
        run('./manage.py migrate {}'.format(app if app else ''))


@task
def update_index():
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    with cd(env.path), prefix(env.within_virtualenv):
        run('./manage.py update_index')


@task
def clear_cache():
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    with cd(env.path), prefix(env.within_virtualenv):
        run('./manage.py clear_cache')


@task
def collect_static(process=False):
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    if env.srvr in ['local', 'vagrant']:
        print((yellow('Do not run collect_static on local servers')))
        return

    with cd(env.path), prefix(env.within_virtualenv):
        run('./manage.py collectstatic {process} --noinput'.format(
            process=('--no-post-process' if not process else '')))


@task
def install_requirements():
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    reqs = 'requirements-{}.txt'.format(env.srvr)

    try:
        assert os.path.exists(reqs)
    except AssertionError:
        reqs = 'requirements.txt'

    with cd(env.path), prefix(env.within_virtualenv):
        run('pip install -U -r {}'.format(reqs))


@task
def reinstall_requirement(which):
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    with cd(env.path), prefix(env.within_virtualenv):
        run('pip uninstall {0} && pip install --no-deps {0}'.format(which))


@task
def own_django_log():
    """ make sure logs/django.log is owned by www-data"""

    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    if env.srvr in ['local', 'vagrant']:
        print((yellow('Do not change ownership of django log on local servers')))
        return
    sudo(
        'chown www-data:www-data {}'.format(
            os.path.join(env.path, 'logs', 'django.log')))


@task
def add_supervisor_conf():
    require('srvr', 'path', provided_by=env.servers)

    sudo('service supervisor stop')

    sudo('ln -f -s {} /etc/supervisor/conf.d'.format(
        os.path.join(env.path,
                     'chopin/supervisor/celery_{}.conf'.format(env.srvr)),
        env.srvr))
    sudo('ln -f -s {} /etc/supervisor/conf.d'.format(
        os.path.join(env.path,
                     'chopin/supervisor/celery_worker_{}.conf'.format(
                         env.srvr)),
        env.srvr))

    with cd(env.path):
        sudo('rm -f celerybeat-schedule')

    sudo('service supervisor start')


@task
def touch_wsgi():
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    with cd(os.path.join(env.path, 'chopin')), prefix(env.within_virtualenv):
        run('touch wsgi.py')


@task
def runserver(port='8000'):
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    if env.srvr not in ['local', 'vagrant']:
        print((yellow('this server only runs for development purposes')))
        return

    with cd(env.path), prefix(env.within_virtualenv):
        run('./manage.py runserver 0.0.0.0:{}'.format(port))

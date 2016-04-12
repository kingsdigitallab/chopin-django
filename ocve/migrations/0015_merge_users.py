__author__ = 'elliotthall'
from django.db import migrations
from django.core.exceptions import ObjectDoesNotExist

import hashlib


def copy_users(apps, schema_editor):
    """Copies user information from OCVEUser to correct merged user model
    model."""
    Annotation = apps.get_model('ocve', 'Annotation')
    BarCollection = apps.get_model('ocve', 'BarCollection')
    #usermanager=apps.get_model('auth', 'UserManager')
    User = apps.get_model('auth', 'User')
    OCVEUser = apps.get_model('ocve', 'OCVEUser')

    #Make sure defaults have been added
    # try:
    #     guest=User.objects.get(username='guest')
    # except ObjectDoesNotExist:
    #     guest=usermanager.create_user('guest', 'guest@chopinonline.ac.uk', 'ThisShouldNotBeUsed')
    #
    # try:
    #     ocve=User.objects.get(username='ocve')
    # except ObjectDoesNotExist:
    #     ocve=User.objects.create_user('ocve', 'info@chopinonline.ac.uk', 'ThisShouldNotBeUsed')
    #     ocve.is_active=False
    #     ocve.save()

    for note in Annotation.objects.all():
        ocveuser=OCVEUser.objects.get(id=note.ocveuser_id)
        users=User.objects.filter(username=ocveuser.username)
        if users.count() > 0:
            note.user=users[0]
            note.save()

    for bc in BarCollection.objects.all():
        ocveuser=OCVEUser.objects.get(id=bc.ocveuser_id)
        users=User.objects.filter(username=ocveuser.username)
        if users.count() > 0:
            bc.user=users[0]
            bc.save()


def reset_users(apps, schema_editor):
    Annotation = apps.get_model('ocve', 'Annotation')
    BarCollection = apps.get_model('ocve', 'BarCollection')
    # User = apps.get_model('auth', 'User')
    #  #Make sure defaults have been added
    # try:
    #     guest=User.objects.get(username='guest')
    # except ObjectDoesNotExist:
    #     guest=User.objects.create_user('guest', 'guest@chopinonline.ac.uk', 'ThisShouldNotBeUsed')

    for bc in BarCollection.objects.all():
        bc.user=guest
        bc.save()
    for note in Annotation.objects.all():
        note.user=guest
        note.save()


class Migration(migrations.Migration):
    dependencies = [
        ('ocve',
         '0014_auto_20151112_1639'),
    ]

    operations = [
        migrations.RunPython(copy_users, reverse_code=reset_users)
    ]


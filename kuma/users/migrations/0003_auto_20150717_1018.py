# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations


def move_to_user(apps, schema_editor):
    UserProfile = apps.get_model('users', 'UserProfile')
    profiles = UserProfile.objects.all()
    count = profiles.count()
    for i, profile in enumerate(profiles.iterator()):
        if i % 10000 == 0:
            print('%d/%d done' % (i, count))
        try:
            user = profile.user
        except ObjectDoesNotExist:
            print('Ignoring profile %s, could not find user %s' %
                  (profile.id, profile.user_id))
            continue
        else:
            user.bio = profile.bio
            user.content_flagging_email = profile.content_flagging_email
            user.fullname = profile.fullname
            user.homepage = profile.homepage
            user.irc_nickname = profile.irc_nickname
            user.locale = profile.locale
            user.location = profile.location
            user.misc = profile.misc
            user.organization = profile.organization
            user.timezone = profile.timezone
            user.title = profile.title
            user.tags = profile.tags
            user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150717_1017'),
    ]

    operations = [
        migrations.RunPython(move_to_user),
    ]

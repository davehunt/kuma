from nose.tools import eq_, ok_
from nose.plugins.attrib import attr

from kuma.wiki.tests import revision

from ..helpers import gravatar_url
from ..models import UserBan, User
from . import UserTestCase


class TestUser(UserTestCase):

    def test_websites(self):
        """A list of websites can be maintained on a user"""
        user = self.user_model.objects.get(username='testuser')

        # Property should start off as an empty dict()
        sites = user.websites
        eq_({}, sites)

        # Assemble a set of test sites.
        test_sites = dict(
            website='http://example.com',
            twitter='http://twitter.com/lmorchard',
            github='http://github.com/lmorchard',
            stackoverflow='http://stackoverflow.com/users/lmorchard',
            mozillians='https://mozillians.org/u/testuser',
            facebook='https://www.facebook.com/test.user'
        )

        # Try a mix of assignment cases for the websites property
        sites['website'] = test_sites['website']
        sites['bad'] = 'bad'
        del sites['bad']
        user.websites['twitter'] = test_sites['twitter']
        user.websites.update(dict(
            github=test_sites['github'],
            stackoverflow=test_sites['stackoverflow'],
            mozillians=test_sites['mozillians'],
            facebook=test_sites['facebook'],
        ))

        # Save and make sure a fresh fetch works as expected
        user.save()
        p2 = User.objects.get(pk=user.pk)
        eq_(test_sites, p2.websites)

        # One more set-and-save to be sure this survives a round-trip
        test_sites['google'] = 'http://google.com'
        p2.websites['google'] = test_sites['google']
        p2.save()
        p3 = User.objects.get(pk=user.pk)
        eq_(test_sites, p3.websites)

    def test_linkedin_urls(self):
        user = self.user_model.objects.get(username='testuser')

        linkedin_urls = [
            'https://in.linkedin.com/in/testuser',
            'https://www.linkedin.com/in/testuser',
            'https://www.linkedin.com/pub/testuser',
        ]

        for url in linkedin_urls:
            user.websites.update(dict(linkedin=url,))
            user.save()
            new_user = User.objects.get(pk=user.pk)
            eq_(url, new_user.websites['linkedin'])

    def test_irc_nickname(self):
        """We've added IRC nickname as a profile field.
        Make sure it shows up."""
        user = self.user_model.objects.get(username='testuser')
        ok_(hasattr(user, 'irc_nickname'))
        eq_('testuser', user.irc_nickname)

    def test_unicode_email_gravatar(self):
        """Bug 689056: Unicode characters in email addresses shouldn't break
        gravatar URLs"""
        user = self.user_model.objects.get(username='testuser')
        user.email = u"Someguy Dude\xc3\xaas Lastname"
        try:
            gravatar_url(user)
        except UnicodeEncodeError:
            self.fail("There should be no UnicodeEncodeError")

    def test_locale_timezone_fields(self):
        """We've added locale and timezone fields. Verify defaults."""
        user = self.user_model.objects.get(username='testuser')
        ok_(hasattr(user, 'locale'))
        ok_(user.locale == 'en-US')
        ok_(hasattr(user, 'timezone'))
        ok_(str(user.timezone) == 'US/Pacific')

    def test_wiki_revisions(self):
        user = self.user_model.objects.get(username='testuser')
        rev = revision(save=True, is_approved=True)
        ok_(rev.pk in user.wiki_revisions().values_list('pk', flat=True))


class BanTestCase(UserTestCase):

    @attr('bans')
    def test_ban_user(self):
        testuser = self.user_model.objects.get(username='testuser')
        admin = self.user_model.objects.get(username='admin')
        ok_(testuser.is_active)
        ban = UserBan(user=testuser,
                      by=admin,
                      reason='Banned by unit test')
        ban.save()
        testuser_banned = self.user_model.objects.get(username='testuser')
        ok_(not testuser_banned.is_active)
        ok_(testuser_banned.is_banned)
        ok_(testuser_banned.active_ban().by == admin)

        ban.is_active = False
        ban.save()
        testuser_unbanned = self.user_model.objects.get(username='testuser')
        ok_(testuser_unbanned.is_active)

        ban.is_active = True
        ban.save()
        testuser_banned = self.user_model.objects.get(username='testuser')
        ok_(not testuser_banned.is_active)
        ok_(testuser_unbanned.is_banned)
        ok_(testuser_unbanned.active_ban())

        ban.delete()
        testuser_unbanned = self.user_model.objects.get(username='testuser')
        ok_(testuser_unbanned.is_active)
        ok_(not testuser_unbanned.is_banned)
        ok_(testuser_unbanned.active_ban() is None)

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import mimetypes

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from audiotracks.models import Track

ITEMS_PER_FEED = getattr(settings, 'AUDIOTRACKS_PODCAST_LIMIT', 20)


class AllTracks(Feed):
    link = "/"

    def title(self):
        return _("%s Podcast") % self._get_site_name()

    def description(self):
        return _("All tracks posted on %s") % self._get_site_name()

    def get_object(self, request):
        self.request = request

    def items(self, user):
        return Track.objects.order_by('-created_at')[:ITEMS_PER_FEED]

    def item_title(self, item):
        return _('"%s" posted by %s') % (item.title, item.user.username)

    def item_description(self, item):
        if item.image:
            return '<img src="%s" alt="%s"/><p>%s</p>' % (
                    self.request.build_absolute_uri(item.image.url_200x200),
                    _("Image for %s") % item.title,
                    item.description
                    )
        else:
            return item.description

    def item_pub_date(self, item):
        return item.created_at

    def item_enclosure_url(self, item):
        return self.request.build_absolute_uri(item.audio_file.url)

    def item_enclosure_length(self, item):
        return item.audio_file.size

    def item_enclosure_mime_type(self, item):
        return mimetypes.guess_type(item.audio_file.path)[0]

    def _get_site_name(self):
        return Site.objects.get_current().name



class UserTracks(AllTracks):

    def get_object(self, request, username):
        self.request = request
        return get_object_or_404(User, username=username)

    def link(self, user):
        return "/%s/" % user.username

    def title(self, user):
        return _("%s Podcast on %s") % (user.username, self._get_site_name())

    def description(self, user):
        return _("Tracks posted on %s by %s" % (self._get_site_name(),
            user.username))

    def items(self, user):
        return Track.objects.filter(user=user).order_by("-created_at")[:ITEMS_PER_FEED]

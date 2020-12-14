#!/usr/bin/python
# -*- coding: utf-8 -*-
r"""
This script can be used for reverting certain edits.

The following command line parameters are supported:

-username         Edits of which user need to be reverted.
                  Default is bot's username (site.username())

-rollback         Rollback edits instead of reverting them.
                  Note that in rollback, no diff would be shown.

-limit:num        Use the last num contributions to be checked for revert.
                  Default is 500.

Users who want to customize the behaviour should subclass the `BaseRevertBot`
and override its `callback` method. Here is a sample:

.. code-block::

    class myRevertBot(BaseRevertBot):

        '''Example revert bot.'''

        def callback(self, item):
            '''Sample callback function for 'private' revert bot.

            @param item: an item from user contributions
            @type item: dict
            @rtype: bool
            '''
            if 'top' in item:
                page = pywikibot.Page(self.site, item['title'])
                text = page.get(get_redirect=True)
                pattern = re.compile(r'\[\[.+?:.+?\..+?\]\]', re.UNICODE)
                return bool(pattern.search(text))
            return False

"""
#
# (C) Bryan Tong Minh, 2008
# (C) Pywikibot team, 2008-2019
#
# Ported by Geoffrey "GEOFBOT" Mon - User:Sn1per
# for Google Code-In 2013
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, division, unicode_literals

import pywikibot

from pywikibot.bot import OptionHandler
from pywikibot import i18n
from pywikibot.tools import deprecate_arg
from pywikibot.tools.formatter import color_format


class BaseRevertBot():

    def __init__(self, site=None, **kwargs):
        """Initializer."""
        self.site = site or pywikibot.Site()
        self.user = "Frettiebot"

    def get_contributions(self):
        """Get contributions."""
        return self.site.usercontribs(user=self.user, start=1572906142, end=1572817200)

    def revert_contribs(self, callback=None):
        for item in self.get_contributions():
            self.revert(item)

    def revert(self, item):
        comment = item['comment']
        # coding=utf8
        # the above tag defines encoding for this document and is for Python 2.x compatibility
        import re

        regex = r"\[\[Property:(.*)\]\]:\W+(.*)"
        matches = re.search(regex, comment)
        grp = matches.groups()
        property = grp[0]
        aut_to_del = grp[1]
        try:
            if (property == "P691"):
                wdpage = pywikibot.ItemPage(self.site, item['title'])
                data = wdpage.get()
                autority = data['claims']['P691']
                claims_to_delete = []
                if (len(autority)):
                    for aut in autority:
                        target = aut.getTarget()
                        if (target == aut_to_del):
                            claims_to_delete.append(aut)
                if (len(claims_to_delete)):
                    wdpage.removeClaims(claims_to_delete, summary="Revert bad NKCR Property:P691: " + aut_to_del)
                    print(claims_to_delete)
        except KeyError as e:
            pass
        except pywikibot.exceptions.IsRedirectPage as e:
            pass

    def log(self, msg):
        """Log the message msg."""
        pywikibot.output(msg)




bot = BaseRevertBot()
bot.revert_contribs()
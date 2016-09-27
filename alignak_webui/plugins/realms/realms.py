#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016:
#   Frederic Mohier, frederic.mohier@gmail.com
#
# This file is part of (WebUI).
#
# (WebUI) is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# (WebUI) is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with (WebUI).  If not, see <http://www.gnu.org/licenses/>.

"""
    Plugin Realm
"""

import json
from logging import getLogger

from bottle import request, template, response

from alignak_webui import _
from alignak_webui.objects.element_state import ElementState
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.plugin import Plugin

logger = getLogger(__name__)


class PluginRealms(Plugin):
    """ Services groups plugin """

    def __init__(self, app, cfg_filenames=None):
        """
        Services groups plugin

        Overload the default get route to declare filters.
        """
        self.name = 'Realms'
        self.backend_endpoint = 'realm'

        self.pages = {
            'get_realm_members': {
                'name': 'Realm members',
                'route': '/realm/members/<element_id>'
            },
        }

        super(PluginRealms, self).__init__(app, cfg_filenames)

    def get_overall_state(self, element_id=None, element=None, no_json=False):
        # pylint: disable=protected-access
        """
        Get the realm overall status
        """
        datamgr = request.app.datamgr

        realm = element
        if not realm:
            realm = datamgr.get_realm(element_id)
            if not realm:
                realm = datamgr.get_realm(
                    search={'max_results': 1, 'where': {'name': element_id}}
                )
                if not realm:
                    return self.webui.response_invalid_parameters(_('Element does not exist: %s')
                                                                  % element_id)

        realm.overall_state = datamgr.get_realm_overall_state(realm)
        logger.debug(" - realm real state: %d -> %s", realm.overall_state, realm.overall_state)

        if no_json:
            return realm.overall_state

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps({'state': realm.overall_state, 'status': realm.overall_state})

    def get_realm_members(self, element_id):
        """
        Get the realm hosts list
        """
        datamgr = request.app.datamgr

        realm = datamgr.get_realm(element_id)
        if not realm:
            realm = datamgr.get_realm(
                search={'max_results': 1, 'where': {'name': element_id}}
            )
            if not realm:
                return self.webui.response_invalid_parameters(_('Element does not exist: %s')
                                                              % element_id)

        # Get elements from the data manager
        search = {
            'where': {'_realm': realm.id}
        }
        hosts = datamgr.get_hosts(search)

        # Get element state configuration
        items_states = ElementState()

        items = []
        for member in hosts:
            logger.debug("Realm member: %s", member)
            cfg_state = items_states.get_icon_state('host', member.status)

            items.append({
                'id': member.id,
                'type': 'host',
                'name': member.name,
                'alias': member.alias,
                'status': member.status,
                'icon': 'fa fa-%s item_%s' % (cfg_state['icon'], cfg_state['class']),
                'state': member.get_html_state(text=None, title=member.alias),
                'url': member.get_html_link()
            })

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(items)

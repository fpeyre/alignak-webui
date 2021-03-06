#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017:
#   Frederic Mohier, frederic.mohier@alignak.net
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
    Plugin users groups
"""

import json
from logging import getLogger

from bottle import request, response

from alignak_webui.objects.element_state import ElementState
from alignak_webui.utils.plugin import Plugin

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginServicesGroups(Plugin):
    """ Services groups plugin """

    def __init__(self, webui, plugin_dir, cfg_filenames=None):
        """
        Services groups plugin

        Overload the default get route to declare filters.
        """
        self.name = 'Users groups'
        self.backend_endpoint = 'usergroup'

        self.pages = {
            'get_usergroup_members': {
                'name': 'Users group members',
                'route': '/usergroup/members/<group_id>'
            },
        }

        super(PluginServicesGroups, self).__init__(webui, plugin_dir, cfg_filenames)

    def get_one(self, element_id):
        """
            Show one element
        """
        datamgr = request.app.datamgr

        # Get elements from the data manager
        f = getattr(datamgr, 'get_%s' % self.backend_endpoint)
        if not f:  # pragma: no cover - should not happen!
            self.send_user_message(_("No method to get a %s element") % self.backend_endpoint)

        logger.debug("get_one, search: %s", element_id)
        element = f(element_id)
        if not element:
            element = f(search={'max_results': 1, 'where': {'name': element_id}})
            if not element:
                self.send_user_message(_("%s '%s' not found") % (self.backend_endpoint, element_id))
        logger.debug("get_one, found: %s - %s", element, element.__dict__)

        groups = element.usergroups
        if element.level == 0:
            groups = datamgr.get_usergroups(search={'where': {'_level': 1}})

        return {
            'object_type': self.backend_endpoint,
            'element': element,
            'groups': groups
        }

    def get_usergroup_members(self, group_id):
        """
        Get the usergroup users list
        """
        datamgr = request.app.datamgr

        usergroup = datamgr.get_usergroup(group_id)
        if not usergroup:
            usergroup = datamgr.get_usergroup(
                search={'max_results': 1, 'where': {'name': group_id}}
            )
            if not usergroup:
                return self.webui.response_invalid_parameters(_('Element does not exist: %s')
                                                              % group_id)

        items = []
        if not isinstance(usergroup.members, basestring):
            # Get element state configuration
            items_states = ElementState()

            for member in usergroup.members:
                logger.debug("Group member: %s", member)
                cfg_state = items_states.get_icon_state('user', member.status)

                items.append({
                    'id': member.id,
                    'type': 'user',
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

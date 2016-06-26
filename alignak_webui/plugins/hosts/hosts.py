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
    Plugin Hosts
"""

import time
import json

from collections import OrderedDict

from logging import getLogger
from bottle import request, template, response

from alignak_webui.objects.item import Item

from alignak_webui.plugins.histories.histories import schema as history_schema

from alignak_webui.utils.datatable import Datatable
from alignak_webui.utils.helper import Helper

logger = getLogger(__name__)

# Will be populated by the UI with it's own value
webui = None

# Get the same schema as the applications backend and append information for the datatable view
# Use an OrderedDict to create an ordered list of fields
schema = OrderedDict()
# Specific field to include the responsive + button used to display hidden columns on small devices
schema['#'] = {
    'type': 'string',
    'ui': {
        'title': '',
        # This field is visible (default: False)
        'visible': True,
        # This field is initially hidden (default: False)
        'hidden': False,
        # This field is searchable (default: True)
        'searchable': False,
        # This field is orderable (default: True)
        'orderable': False,
        # search as a regex (else strict value comparing when searching is performed)
        'regex': False,
        # defines the priority for the responsive column hidding (0 is the most important)
        # Default is 10000
        # 'priority': 0,
    }
}
schema['name'] = {
    'type': 'string',
    'ui': {
        'title': _('Host name'),
        # This field is visible (default: False)
        'visible': True,
        # This field is initially hidden (default: False)
        'hidden': False,
        # This field is searchable (default: True)
        'searchable': True,
        # search as a regex (else strict value comparing when searching is performed)
        'regex': True,
        # This field is orderable (default: True)
        'orderable': True,
    },
}
schema['definition_order'] = {
    'type': 'integer',
    'ui': {
        'title': _('Definition order'),
        'visible': True,
        'hidden': True,
        'orderable': False,
    },
}
schema['alias'] = {
    'type': 'string',
    'ui': {
        'title': _('Host alias'),
        'visible': True
    },
}
schema['display_name'] = {
    'type': 'string',
    'ui': {
        'title': _('Host display name'),
        'visible': True
    },
}
schema['address'] = {
    'type': 'string',
    'ui': {
        'title': _('Address'),
        'visible': True
    },
}
schema['check_command'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Check command'),
        'visible': True
    },
    'data_relation': {
        'resource': 'command',
        'embeddable': True
    }
}
schema['check_command_args'] = {
    'type': 'string',
    'ui': {
        'title': _('Check command arguments'),
        'visible': True
    },
}
schema['check_period'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Check period'),
        'visible': True
    },
    'data_relation': {
        'resource': 'timeperiod',
        'embeddable': True
    }
}
schema['check_interval'] = {
    'type': 'integer',
    'ui': {
        'title': _('Check interval'),
        'visible': True
    },
}
schema['retry_interval'] = {
    'type': 'integer',
    'ui': {
        'title': _('Retry interval'),
        'visible': True
    },
}
schema['max_check_attempts'] = {
    'type': 'integer',
    'ui': {
        'title': _('Maximum check attempts'),
        'visible': True
    },
}
schema['active_checks_enabled'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Active checks enabled'),
        'visible': True
    },
}
schema['passive_checks_enabled'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Passive checks enabled'),
        'visible': True
    },
}
schema['parents'] = {
    'type': 'list',
    'ui': {
        'title': _('Parents'),
        'visible': True
    },
    'data_relation': {
        'resource': 'host',
        'embeddable': True
    }
}
schema['hostgroups'] = {
    'type': 'list',
    'ui': {
        'title': _('Hosts groups'),
        'visible': True
    },
    'data_relation': {
        'resource': 'hostgroup',
        'embeddable': True
    }
}
schema['business_impact'] = {
    'type': 'integer',
    'ui': {
        'title': _('Business impact'),
        'visible': True
    },
}
schema['contacts'] = {
    'type': 'list',
    'ui': {
        'title': _('Users'),
        'visible': True
    },
    'data_relation': {
        'resource': 'contact',
        'embeddable': True
    }
}
schema['contact_groups'] = {
    'type': 'list',
    'ui': {
        'title': _('Users groups'),
        'visible': True
    },
    'data_relation': {
        'resource': 'contactgroup',
        'embeddable': True
    }
}
schema['notifications_enabled'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Notifications enabled'),
        'visible': True
    },
}
schema['notification_period'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Notification period'),
        'visible': True
    },
    'data_relation': {
        'resource': 'timeperiod',
        'embeddable': True
    }
}
schema['notification_interval'] = {
    'type': 'integer',
    'ui': {
        'title': _('Notification interval'),
        'visible': True
    },
}
schema['first_notification_delay'] = {
    'type': 'integer',
    'ui': {
        'title': _('First notification delay'),
        'visible': True
    },
}
schema['notification_options'] = {
    'type': 'list',
    'default': ['o', 'd', 'u'],
    'allowed': ['o', 'd', 'u'],
    'ui': {
        'title': _('Flapping detection options'),
        'visible': True,
        'format': {
            'list_type': "multichoices",
            'list_allowed': {
                u"d": u"Send notifications on Down state",
                u"r": u"Send notifications on recoveries",
                u"u": u"Send notifications on Unreachable state",
                u"f": u"Send notifications on flapping start/stop",
                u"s": u"Send notifications on scheduled downtime start/stop",
                u"n": u"Do not send notifications"
            }
        }
    },
}
schema['location'] = {
    'type': 'point',
    'ui': {
        'title': _('Location')
    }
}
schema['notes'] = {
    'type': 'string',
    'ui': {
        'title': _('Notes')
    }
}
schema['notes_url'] = {
    'type': 'string',
    'ui': {
        'title': _('Notes URL')
    }
}
schema['action_url'] = {
    'type': 'string',
    'ui': {
        'title': _('Action URL')
    }
}
schema['stalking_options'] = {
    'type': 'list',
    'default': [],
    'allowed': ['o', 'd', 'u'],
    'ui': {
        'title': _('Flapping detection options'),
        'visible': True,
        'format': {
            'list_type': "multichoices",
            'list_allowed': {
                u"d": u"Down",
                u"o": u"Up",
                u"u": u"Unreachable"
            }
        }
    },
}
schema['check_freshness'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Freshness check enabled'),
        'visible': True
    },
}
schema['freshness_threshold'] = {
    'type': 'integer',
    'ui': {
        'title': _('Freshness threshold'),
        'visible': True
    },
}
schema['flap_detection_enabled'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Flapping detection enabled'),
        'visible': True
    },
}
schema['flap_detection_options'] = {
    'type': 'list',
    'default': ['o', 'd', 'u'],
    'allowed': ['o', 'd', 'u'],
    'ui': {
        'title': _('Flapping detection options'),
        'visible': True
    },
}
schema['low_flap_threshold'] = {
    'type': 'integer',
    'ui': {
        'title': _('Low flapping threshold'),
        'visible': True,
        'hidden': True,
    },
}
schema['high_flap_threshold'] = {
    'type': 'integer',
    'ui': {
        'title': _('High flapping threshold'),
        'visible': True,
        'hidden': True,
    },
}
schema['event_handler_enabled'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Event handler enabled'),
        'visible': True
    },
}
schema['event_handler'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Event handler command'),
        'visible': True
    },
    'data_relation': {
        'resource': 'command',
        'embeddable': True
    }
}
schema['process_perf_data'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Process performance data'),
        'visible': True
    },
}


# This to define the global information for the table
schema['ui'] = {
    'type': 'boolean',
    'default': True,

    # UI parameters for the objects
    'ui': {
        'page_title': _('Hosts table (%d items)'),
        'uid': '_id',
        'visible': True,
        'orderable': True,
        'editable': False,
        'selectable': True,
        'searchable': True,
        'responsive': True
    }
}


def get_hosts():
    """
    Get the hosts list
    """
    user = request.environ['beaker.session']['current_user']
    datamgr = request.environ['beaker.session']['datamanager']
    target_user = request.environ['beaker.session']['target_user']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    # Fetch elements per page preference for user, default is 25
    elts_per_page = datamgr.get_user_preferences(username, 'elts_per_page', 25)
    elts_per_page = elts_per_page['value']

    # Pagination and search
    start = int(request.query.get('start', '0'))
    count = int(request.query.get('count', elts_per_page))
    where = webui.helper.decode_search(request.query.get('search', ''))
    search = {
        'page': start // count + 1,
        'max_results': count,
        'sort': '-_id',
        'where': where,
        'embedded': {
            'check_command': 1, 'event_handler': 1,
            'check_period': 1, 'notification_period': 1,
            'parents': 1, 'hostgroups': 1, 'contacts': 1, 'contact_groups': 1
        }
    }

    # Get elements from the data manager
    hosts = datamgr.get_hosts(search)
    # Get last total elements count
    total = datamgr.get_objects_count('host', search=where, refresh=True)
    count = min(count, total)

    return {
        'hosts': hosts,
        'pagination': Helper.get_pagination_control('/hosts', total, start, count),
        'title': request.query.get('title', _('All hosts'))
    }


def get_hosts_widget():
    # Because there are many locals needed :)
    # pylint: disable=too-many-locals
    """
    Get the hosts list as a widget
    - widget_id: widget identifier

    - start and count for pagination
    - search for specific elements search

    """
    user = request.environ['beaker.session']['current_user']
    datamgr = request.environ['beaker.session']['datamanager']
    target_user = request.environ['beaker.session']['target_user']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    # Fetch elements per page preference for user, default is 25
    elts_per_page = datamgr.get_user_preferences(username, 'elts_per_page', 25)
    elts_per_page = elts_per_page['value']

    # Pagination and search
    start = int(request.forms.get('start', '0'))
    count = int(request.forms.get('count', elts_per_page))
    where = webui.helper.decode_search(request.forms.get('search', ''))
    search = {
        'page': start // count + 1,
        'max_results': count,
        'sort': '-_id',
        'where': where,
        'embedded': {
            'check_command': 1, 'event_handler': 1,
            'check_period': 1, 'notification_period': 1,
            'parents': 1, 'hostgroups': 1, 'contacts': 1, 'contact_groups': 1
        }
    }
    name_filter = request.forms.get('filter', '')
    if name_filter:
        search['where'].update({'name': {"$regex": ".*" + name_filter + ".*"}})

    # Get elements from the data manager
    hosts = datamgr.get_hosts(search)
    # Get last total elements count
    total = datamgr.get_objects_count('host', search=where, refresh=True)
    count = min(count, total)

    # Widget options
    widget_id = request.forms.get('widget_id', '')
    if widget_id == '':
        return webui.response_invalid_parameters(_('Missing widget identifier'))
    widget_template = request.forms.get('widget_template', '')
    if widget_template == '':
        return webui.response_invalid_parameters(_('Missing widget template'))

    widget_place = request.forms.get('widget_place', 'dashboard')
    # Search in the application widgets (all plugins widgets)
    options = {}
    for widget in webui.widgets[widget_place]:
        if widget_id.startswith(widget['id']):
            options = widget['options']

    if options.get('search') and options.get('search.value'):
        search.options.value = request.forms.get('search', '')
    if options.get('count') and options.get('count.value'):
        search['options']['value'] = count
    if options.get('filter') and options.get('filter.value'):
        search['options']['filter'] = name_filter

    title = request.forms.get('title', _('Hosts'))
    if name_filter:
        title = _('%s (%s)') % (title, name_filter)

    # Use required template to render the widget
    return template(widget_template, {
        'widget_id': widget_id,
        'widget_place': widget_place,
        'widget_template': widget_template,
        'widget_uri': request.urlparts.path,
        'hosts': hosts,
        'options': options,
        'title': title
    })


def get_hosts_table():
    """
    Get the hosts list and transform it as a table
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Pagination and search
    where = Helper.decode_search(request.query.get('search', ''))

    # Get total elements count
    total = datamgr.get_objects_count('host', search=where)

    # Build table structure
    dt = Datatable('host', datamgr.backend, schema)

    title = dt.title
    if '%d' in title:
        title = title % total

    return {
        'object_type': 'host',
        'dt': dt,
        'where': where,
        'title': request.query.get('title', title)
    }


def get_hosts_table_data():
    """
    Get the hosts list and provide table data
    """
    datamgr = request.environ['beaker.session']['datamanager']
    dt = Datatable('host', datamgr.backend, schema)

    response.status = 200
    response.content_type = 'application/json'
    return dt.table_data()


def get_host(host_id):
    # Because there are many locals needed :)
    # pylint: disable=too-many-locals
    """
    Display an host
    """
    user = request.environ['beaker.session']['current_user']
    datamgr = request.environ['beaker.session']['datamanager']
    target_user = request.environ['beaker.session']['target_user']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    host = datamgr.get_host(host_id)
    if not host:  # pragma: no cover, should not happen
        return webui.response_invalid_parameters(_('Host does not exist'))

    services = datamgr.get_services(search={'where': {'host': host_id}})
    livestate = datamgr.get_livestate(search={'where': {'type': 'host', 'name': '%s' % host.name}})
    if livestate:
        livestate = livestate[0]

    # Fetch elements per page preference for user, default is 25
    elts_per_page = datamgr.get_user_preferences(username, 'elts_per_page', 25)
    elts_per_page = elts_per_page['value']

    # Host history pagination and search parameters
    start = int(request.query.get('start', '0'))
    count = int(request.query.get('count', elts_per_page))
    where = webui.helper.decode_search(request.query.get('search', ''))
    search = {
        'where': {'host': host_id},
        'page': start // count + 1,
        'max_results': count,
        'sort': '-_created'
    }

    # Fetch timeline filters preference for user, default is []
    selected_types = datamgr.get_user_preferences(username, 'timeline_filters', [])
    selected_types = selected_types['value']
    for selected_type in history_schema['type']['allowed']:
        if request.query.get(selected_type) == 'true':
            if selected_type not in selected_types:
                selected_types.append(selected_type)
            logger.critical("Filter: %s=%s", selected_type, request.query.get(selected_type))
        elif request.query.get(selected_type) == 'false':
            if selected_type in selected_types:
                selected_types.remove(selected_type)

    if selected_types:
        datamgr.set_user_preferences(username, 'timeline_filters', selected_types)
        search['where'].update({'type': {'$in': selected_types}})
    logger.debug("History selected types: %s", selected_types)

    history = datamgr.get_history(search=search)
    if history is None:
        history = []

    # Get last total elements count
    total = datamgr.get_objects_count('history', search=where, refresh=True)

    return {
        'host': host,
        'services': services,
        'livestate': livestate,
        'history': history,
        'timeline_pagination': Helper.get_pagination_control('/host/' + host_id,
                                                             total, start, count),
        'types': history_schema['type']['allowed'],
        'selected_types': selected_types,
        'title': request.query.get('title', _('Host view'))
    }


pages = {
    get_host: {
        'name': 'Host',
        'route': '/host/<host_id>',
        'view': 'host'
    },
    get_hosts: {
        'name': 'Hosts',
        'route': '/hosts',
        'view': 'hosts',
        'search_engine': True,
        'search_prefix': '',
        'search_filters': {
            _('Hosts up'): 'state:up',
            _('Hosts down'): 'state:down',
            _('Hosts unreachable'): 'state:unreachable',
        }
    },
    get_hosts_table: {
        'name': 'Hosts table',
        'route': '/hosts_table',
        'view': '_table'
    },

    get_hosts_table_data: {
        'name': 'Hosts table data',
        'route': '/host_table_data',
        'method': 'POST'
    },

    get_hosts_widget: {
        'name': 'Hosts widget',
        'route': '/hosts/widget',
        'method': 'POST',
        'view': 'hosts_widget',
        'widgets': [
            {
                'id': 'hosts_table',
                'for': ['dashboard'],
                'name': _('Hosts table widget'),
                'template': 'hosts_table_widget',
                'icon': 'table',
                'description': _(
                    '<h4>Hosts table widget</h4>Display a list of the monitored system hosts.<br>'
                    'The number of hosts in this list can be defined in the widget options.'
                    'The list of hosts can be filtered thanks to regex on the host name'
                ),
                'picture': 'htdocs/img/hosts_table_widget.png',
                'options': {
                    'search': {
                        'value': '',
                        'type': 'text',
                        'label': _('Filter (ex. status:up)')
                    },
                    'count': {
                        'value': -1,
                        'type': 'int',
                        'label': _('Number of elements')
                    },
                    'filter': {
                        'value': '',
                        'type': 'hst_srv',
                        'label': _('Host name search')
                    }
                }
            },
            {
                'id': 'hosts_graph',
                'for': ['dashboard'],
                'name': _('Hosts chart widget'),
                'template': 'hosts_chart_widget',
                'icon': 'pie-chart',
                'description': _(
                    '<h4>Hosts chart widget</h4>Display a pi chart with the system hosts states.'
                ),
                'picture': 'htdocs/img/hosts_chart_widget.png',
                'options': {}
            }
        ]
    },
}

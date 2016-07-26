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
    This module contains functions used to compute values from performance data metrics.

    Those functions are mainly used in the Host view panel.
"""
import re
from logging import getLogger

from alignak_webui.utils.perfdata import PerfDatas

logger = getLogger(__name__)


# Get plugin's parameters from configuration file
# Define service/perfdata name for each element in graph
class HostMetrics(object):
    """
    Helper functions
    """
    def __init__(self, host, services, params, tags=[]):
        """
        """
        # Default values
        self.params = {}
        self.tags = []
        if tags:
            self.tags = tags
        for param in params:
            p = param.split('.')
            if p[0] not in self.tags:
                continue
            if p[2] not in ['name', 'type', 'metrics', 'uom']:
                continue

            logger.debug("metrics, service match: %s=%s", param, params[param])
            service = p[1]
            if not service in self.params:
                self.params[service] = {}
            self.params[service][p[2]] = params[param]
        logger.debug("metrics, services match configuration: %s", self.params)

        self.host = host
        self.services = services

    def find_service_by_name(self, searched):
        """
        Find a service by its name with regex
        """
        for service in self.services:
            if re.search(searched['name'], service.name):
                return service

        return None

    def get_service_metric(self, service):
        """
        Get a specific service state and metrics

        Returns a tuple built with:
        - service state
        - service name
        - metrics common minimum value (all metrics share the same minimum)
        - metrics common maximum value (all metrics share the same maximum)
        - metrics common warning value (all metrics share the same warning)
        - metrics common critical value (all metrics share the same critical)
        - list of metrics dict, including name, value, min, max, warning, critical, and uom)
        """
        data = []
        state = -1
        name = 'Unknown'
        min = -1
        max = -1
        warning = -1
        critical = -1

        logger.debug("metrics, get_service_metric for %s (%s)", service, self.params[service])
        if self.params[service]['name'] == 'host_check':
            s = self.host
        else:
            s = self.find_service_by_name(self.params[service])

        if s:
            logger.debug("metrics, matching service: %s", s.name)
            name = s.name
            state = s.state_id
            if s.acknowledged:
                state = 4
            if s.downtime:
                state = 5

            try:  # pragma: no cover - no existing data when testing :(
                p = PerfDatas(s.perf_data)
                logger.debug("metrics, service perfdata: %s", p.__dict__)
                for m in sorted(p):
                    logger.debug("metrics, service perfdata metric: %s", m.__dict__)
                    if m.name and m.value is not None:
                        if re.search(self.params[service]['metrics'], m.name) and \
                           re.match(self.params[service]['uom'], m.uom):
                            logger.debug(
                                "metrics, matching metric: '%s' = %s", m.name, m.value
                            )
                            data.append(m)
                            if m.min is not None:
                                if min == -1:
                                    min = m.min
                                if min != -1 and min != m.min:
                                    min = -2
                            if m.max is not None:
                                if max == -1:
                                    max = m.max
                                if max != -1 and max != m.max:
                                    max = -2
                            if m.warning is not None:
                                if warning == -1:
                                    warning = m.warning
                                if warning != -1 and warning != m.warning:
                                    warning = -2
                            if m.critical is not None:
                                if critical == -1:
                                    critical = m.critical
                                if critical != -1 and critical != m.critical:
                                    critical = -2
            except Exception as exp:
                logger.warning("metrics get_service_metric, exception: %s", str(exp))

        logger.debug("metrics, get_service_metric %s", data)
        return state, name, min, max, warning, critical, data

    def get_overall_state(self):
        """
        Get the host and its services global state

        Returns a list of tuples with first tuple as the host state:
        [
            (hostname, host global state),
            (service name, service state),
            ...
        ]

        The state is an integer:
        - 0: OK/UP
        - 1: WARNING/DOWN
        - 2: CRITICAL/UNREACHABLE
        - 3: UNKNOWN
        - 4: ACK
        - 5: DOWNTIME
        """
        data = []
        state = self.host.state_id
        if self.host.acknowledged:
            state = 4
        if self.host.downtime:
            state = 5

        # Get host's services list
        for s in self.services:
            s_state = s.state_id
            if s.acknowledged:
                s_state = 4
            if s.downtime:
                s_state = 5

            data.append((s.name, s_state))
            state = max(state, s_state)

        data =  [(self.host.name, state)] + data
        logger.debug("metrics, get_services %d, %s", state, data)
        return data

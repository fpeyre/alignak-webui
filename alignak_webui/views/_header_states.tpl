%setdefault('datamgr', None)

%if datamgr:
%import time
%from alignak_webui.objects.item_host import Host
%from alignak_webui.objects.item_service import Service

%lv = datamgr.get_livesynthesis()
%hs = lv['hosts_synthesis']

%from bottle import request
%if request.app.config.get('header_refresh_period', '30') != '0':
%# Store N last livesynthesis in a user preference ... this to allow charting last minutes activity.
%hosts_states_queue = datamgr.get_user_preferences(current_user, 'hosts_states_queue', [])
%hosts_states_queue.append({'date': time.time(), 'hs': hs})
%if len(hosts_states_queue) > 120:
%hosts_states_queue.pop(0)
%end
%datamgr.set_user_preferences(current_user, 'hosts_states_queue', hosts_states_queue)
%end

%ss = lv['services_synthesis']

%from bottle import request
%if request.app.config.get('header_refresh_period', '30') != '0':
%# Store N last livesynthesis in a user preference ... this to allow charting last minutes activity.
%services_states_queue = datamgr.get_user_preferences(current_user, 'services_states_queue', [])
%services_states_queue.append({'date': time.time(), 'ss': ss})
%if len(services_states_queue) > 120:
%services_states_queue.pop(0)
%end
%datamgr.set_user_preferences(current_user, 'services_states_queue', services_states_queue)
%end

<div id="hosts-states-popover-content" class="hidden">
   <table class="table table-invisible">
      <tbody>
         <tr>
            %for state in ['up', 'unreachable', 'down']:
            <td>
              %title = _('%s hosts %s (%s%%)') % (hs["nb_" + state], state, hs["pct_" + state])
              %label = "%s <i>(%s%%)</i>" % (hs["nb_" + state], hs["pct_" + state])
               <a href="{{ webui.get_url('Livestate table') }}?search=type:host state:{{state.upper()}}">
              {{! Host({'status':state}).get_html_state(text=label, title=title, disabled=(not hs["nb_" + state]))}}
               </a>
            </td>
            %end
         </tr>
      </tbody>
   </table>
</div>

<li id="overall-hosts-states" class="pull-left">
%font='danger' if hs['pct_problems'] >= hs['critical_threshold'] else 'warning' if hs['pct_problems'] >= hs['warning_threshold'] else 'success'
%from alignak_webui.objects.element_state import ElementState
%items_states = ElementState()
%cfg_state = items_states.get_icon_state('host', 'up')
%icon = cfg_state['icon']
<a id="hosts-states-popover"
   href="#"
   title="{{_('Overall hosts states: %d hosts (%d problems)') % (hs['nb_elts'], hs['nb_problems'])}}"
   data-count="{{ hs['nb_elts'] }}"
   data-problems="{{ hs['nb_problems'] }}"
   data-original-title="{{_('Hosts states')}}"
   data-toggle="popover"
   data-html="true"
   data-trigger="hover focus">
   <span class="fa fa-{{icon}}"></span>
   <span class="label label-as-badge label-{{font}}">{{hs["nb_problems"] if hs["nb_problems"] > 0 else ''}}</span>
</a>
</li>

<script>
   // Activate the popover ...
   $('#hosts-states-popover').popover({
      placement: 'bottom',
      animation: true,
      template: '<div class="popover popover-hosts"><div class="arrow"></div><div class="popover-inner"><div class="popover-title"></div><div class="popover-content"></div></div></div>',
      content: function() {
         return $('#hosts-states-popover-content').html();
      }
   });
</script>

<li id="overall-services-states" class="pull-left">
<div id="services-states-popover-content" class="hidden">
   <table class="table table-invisible">
      <tbody>
         <tr>
            %for state in ['ok', 'warning', 'critical', 'unknown']:
            <td>
              %title = _('%s services %s (%s%%)') % (ss["nb_" + state], state, ss["pct_" + state])
              %label = "%s <i>(%s%%)</i>" % (ss["nb_" + state], ss["pct_" + state])
               <a href="{{ webui.get_url('Livestate table') }}?search=type:service state:{{state.upper()}}">
              {{! Service({'status':state}).get_html_state(text=label, title=title, disabled=(not ss["nb_" + state]))}}
               </a>
            </td>
            %end
         </tr>
      </tbody>
   </table>
</div>

%font='danger' if ss['pct_problems'] >= ss['critical_threshold'] else 'warning' if ss['pct_problems'] >= ss['warning_threshold'] else 'success'
%from alignak_webui.objects.element_state import ElementState
%items_states = ElementState()
%cfg_state = items_states.get_icon_state('service', 'ok')
%icon = cfg_state['icon']
<a id="services-states-popover"
   href="#"
   title="{{_('Overall services states: %d services (%d problems)') % (ss['nb_elts'], ss['nb_problems'])}}"
   data-count="{{ ss['nb_elts'] }}"
   data-problems="{{ ss['nb_problems'] }}"
   data-original-title="{{_('Services states')}}"
   data-toggle="popover"
   data-html="true"
   data-trigger="hover focus">
   <span class="fa fa-{{icon}}"></span>
   <span class="label label-as-badge label-{{font}}">{{ss["nb_problems"] if ss["nb_problems"] else ''}}</span>
</a>
</li>

<script>
   // Activate the popover ...
   $('#services-states-popover').popover({
      placement: 'bottom',
      animation: true,
      template: '<div class="popover popover-services"><div class="arrow"></div><div class="popover-inner"><div class="popover-title"></div><div class="popover-content"></div></div></div>',
      content: function() {
         return $('#services-states-popover-content').html();
      }
   });
</script>

%end

<!-- Hosts view widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.metrics import HostMetrics
%metrics = HostMetrics(livestate, livestate_services, hosts_parameters, host.tags)
%services_states = metrics.get_overall_state()
%host_name, host_state = services_states[0]
%services_states = services_states[1:]

<div id="host_view_information" class="col-lg-4 col-sm-4 text-center">
   {{! livestate.get_html_state(text=None, size="fa-5x")}}
   <div>
      <strong>{{host.alias}}</strong>
   </div>
   %if livestate_services:
   <div class="text-left">
      <table class="table table-condensed">
         <thead><tr>
            <th style="width: 40px"></th>
            <th></th>
         </tr></thead>

         <tbody>
            %for lv_service in livestate_services:
            <tr id="#{{lv_service.id}}">
               <td title="{{lv_service.alias}}">
                  %title = "%s - %s (%s)" % (lv_service.status, Helper.print_duration(lv_service.last_check, duration_only=True, x_elts=0), lv_service.output)
                  {{! lv_service.get_html_state(text=None, title=title)}}
               </td>

               <td>
                  <small>{{! lv_service.get_html_link()}}</small>
               </td>
            </tr>
            %end
         </tbody>
      </table>
   </div>
   %end
</div>
<div id="host_view_graphes" class="col-lg-8 col-sm-8">
   %if not services:
   <center>
      <h3>{{_('No services defined for this host.')}}</h3>
   </center>
   %else:
      %for svc in metrics.params:
         %svc_state, svc_name, svc_min, svc_max, svc_warning, svc_critical, svc_metrics = metrics.get_service_metric(svc)
         %if svc_state == -1:
         %continue
         %end
         <div id="bc_{{svc}}" class="well well-sm test">
            <div class="graph">
               <canvas></canvas>
            </div>
         </div>
      %end
   %end
</div>

%if services:
<script>
   var state_colors = [
      '#ddffcc', '#ffd9b3', '#ffb3b3', '#b3d9ff', '#dddddd', '#666666'
   ];
   var bar_backgroundColor = "rgba(0, 0, 0, 0.3)";
   var bar_borderColor = "#0000b3";
   var bar_hoverBackgroundColor = "rgba(255,99,132,0.4)";
   var bar_hoverBorderColor = "rgba(255,99,132,1)";

   // Fix for pie/doughnut with a percentage ...
   Chart.controllers.doughnut.prototype.calculateTotal = function() { return 100; }

   $(document).ready(function() {
      %for svc in sorted(metrics.params):
         %svc_state, svc_name, svc_min, svc_max, svc_warning, svc_critical, svc_metrics = metrics.get_service_metric(svc)
         %if svc_state == -1:
         %continue
         %end

         var data=[], labels=[], warning=[], critical=[];
         %chart_type = metrics.params[svc].get('type', 'bar')
         %sum_values = 0
         %for perf in sorted(svc_metrics):
            labels.push("{{perf.name}}");
            data.push({{perf.value}});
            warning.push({{perf.warning}});
            critical.push({{perf.critical}});
            %sum_values += perf.value
         %end
         %if chart_type == 'gauge':
            //data.push({{100 - sum_values}});
         %end
         var data = {
            labels: labels,
            datasets: [
               {
                  label: '{{svc_name}}',
                  backgroundColor: bar_backgroundColor,
                  borderColor: bar_borderColor,
                  borderWidth: 1,
                  hoverBackgroundColor: bar_hoverBackgroundColor,
                  hoverBorderColor: bar_hoverBorderColor,
                  data: data,
               }
               %if chart_type == 'bar' or chart_type == 'horizontalBar':
               %if svc_warning >= 0:
               ,{
                  label: 'Warning',
                  type: 'line',
                  fill: false,
                  //backgroundColor: "rgba(151,187,205,0.5)",
                  borderColor: state_colors[1],
                  borderWidth: 2,
                  pointBorderColor: state_colors[2],
                  pointBorderWidth: 2,
                  showLine: false,
                  data: warning,
               }
               %end
               %if svc_critical >= 0:
               ,{
                  label: 'Critical',
                  type: 'line',
                  fill: false,
                  //backgroundColor: "rgba(151,187,205,0.5)",
                  borderColor: state_colors[2],
                  borderWidth: 2,
                  pointBorderColor: state_colors[2],
                  pointBorderWidth: 2,
                  showLine: false,
                  data: critical
               }
               %end
               %end
            ]
         };
         var ctx = $("#bc_{{svc}} canvas");
         // Set color depending upon state
         ctx.css({'backgroundColor': state_colors[{{svc_state}}]});
         var myChart = new Chart(ctx, {
            %if chart_type == 'gauge':
            type: 'doughnut',
            %else:
            type: '{{metrics.params[svc].get('type', 'bar')}}',
            %end
            data: data,
            options: {
               %if chart_type == 'gauge':
                  rotation: Math.PI,
                  circumference: Math.PI,
               %end
               title: {
                  display: true,
                  text: '{{svc_name}}'
               },
               %if chart_type != 'pie' and chart_type != 'gauge':
               scales: {
                  %if chart_type == 'horizontalBar':
                  xAxes: [{
                  %else:
                  yAxes: [{
                  %end
                     stacked: false,
                     ticks: {
                        %if svc_min >= 0:
                        min: {{svc_min}},
                        %end
                        %if svc_max >= 0:
                        max: {{svc_max}},
                        %end
                     }
                  }]
               }
               ,animation: {
                  onComplete: function () {
                     var chartInstance = this.chart;
                     var ctx = chartInstance.ctx;
                     ctx.textAlign = "center";
                     Chart.helpers.each(this.data.datasets.forEach(function (dataset, i) {
                        var meta = chartInstance.controller.getDatasetMeta(i);
                        Chart.helpers.each(meta.data.forEach(function (bar, index) {
                           ctx.fillText(dataset.data[index], bar._model.x - 10, bar._model.y - 10);
                        }),this)
                     }),this);
                  }
               }
               %end
            }
         });
      %end

      $(window).resize();
   });
</script>
%end
<!-- Hosts history widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%#Only ack events...
%history_filter = []
%if history:
   %include("histories.tpl", histories=events, filter=history_filter, layout=False, pagination=Helper.get_pagination_control('history', len(history), 0, len(history)))
%else:
   <div class="alert alert-info">
      <p class="font-blue">{{_('No history logs available.')}}</p>
   </div>
%end

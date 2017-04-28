var markerIcon = [];

{% for marker in markers %}
// {{ marker.name }}
markerIcon[{{ marker.id }}] = L.AwesomeMarkers.icon({
    icon: '{{ marker.icon }}',
    markerColor: '{{ marker.markerColor }}',
    prefix: 'fa'
  });
{% endfor %}

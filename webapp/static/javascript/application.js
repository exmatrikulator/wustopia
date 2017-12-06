var wustopia = {
  marker: [],
  markerIcon: [],
  map: {},
  user: {
    built: [],
    places: []
  },
  session: {
    lat: 0,
    lon: 0,
    acc: null
  }
};

var get_time_as_string = function(time)
{
  var output = "";
  var hours = Math.floor(time / 3600);
  var minutes = Math.floor((time - (hours * 3600)) / 60);
  var seconds = time - (hours * 3600) - (minutes * 60);
  if( hours > 0)
    output += hours + "h ";
  if( minutes > 0)
    output += minutes + "m ";
  if( hours == 0)
    output += seconds + "s";
  return output.trim();
}

//only for testing
var test_time = function()
{
  if(
    get_time_as_string(5) == "5s" &&
    get_time_as_string(10) == "10s" &&
    get_time_as_string(60) == "1m 0s" &&
    get_time_as_string(61) == "1m 1s" &&
    get_time_as_string(130) == "2m 10s" &&
    get_time_as_string(600) == "10m 0s" &&
    get_time_as_string(3600) == "1h" &&
    get_time_as_string(3604) == "1h" &&
    get_time_as_string(3660) == "1h 1m")
    {
      return true;
  }
  else {
    return false;
  }
}

var is_update_places = false;
var update_places = function() {
  if (is_update_places)
    return;
  if (wustopia.map.getZoom() < 17)
    return;
  is_update_places = true;
  var bounds = wustopia.map.getBounds();
  var lng1 = bounds.getSouthWest().lng;
  var lat1 = bounds.getSouthWest().lat;
  var lng2 = bounds.getNorthEast().lng;
  var lat2 = bounds.getNorthEast().lat;
  $.get("update_places/" + lat1 + "," + lng1 + "," + lat2 + "," + lng2, function(data) {
    is_update_places = false;
  });
}

function get_places() {
  if (wustopia.session.lat && wustopia.session.lat) {
    $.getJSON("/api/places", {
      lat: wustopia.session.lat,
      lon: wustopia.session.lon
    }).done(function(data) {
      wustopia.user.places = data;
      data.forEach(function(item) {
        addItem(item);
      })
    });
  }
}

var init = function(position) {

  if (position.coords) {
    wustopia.session.lat = position.coords.latitude;
    wustopia.session.lon = position.coords.longitude;
    wustopia.session.acc = position.coords.accuracy;
    zoom = Math.round(18 - Math.log(wustopia.session.acc) / 10);
  } else {
    zoom = 2;
  }
  get_places();

  $.getJSON("/api/markerIcon", {}).done(function(data) {
    data.forEach(function(item) {
      wustopia.markerIcon[item.id] = L.AwesomeMarkers.icon(item);
    })
  });

  wustopia.map.setView([wustopia.session.lat, wustopia.session.lon], zoom);
  L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(wustopia.map);

  L.marker([wustopia.session.lat, wustopia.session.lon], {
      icon: L.icon({
        iconUrl: ('http://upload.wikimedia.org/wikipedia/commons/c/cb/Icon_person_abstract_blue.jpg'),
        iconSize: [40, 40]
      })
    }).addTo(wustopia.map)
    .bindPopup('You')
    .openPopup();

  wustopia.map.on("move", update_places);
}


function update_resources() {

  $.getJSON("/api/resources").done(function(data) {
    wustopia.user.resources = data;
    $("#resources").html("");
    data.forEach(function(item) {
      if (item.major) {
        resclass = "resource";
      } else {
        resclass = "resource_hidden";
      }
      jQuery("<div/>", {
        id: "res_" + item.id,
        class: resclass,
        title: item.name
      }).appendTo("#resources");
      jQuery("<img/>", {
        src: item.image
      }).appendTo("#res_" + item.id);
      $("#res_" + item.id).append("  " + item.amount);
    })
  });
}

$(document).ready(function() {
  wustopia.map = L.map('map');
  scaleMap();
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(init, init);
    update_resources();
  }
});

var earn = function(el) {
  //do not collect non buildings
  if (el.target.place.level == 0) {
    return;
  }

  id = el.target.place.id;
  $.get("/earn", {
    'place': id
  }, function(data) {
    if (data == "success") update_resources();
    else if (data != "") wustopia.marker[id].setPopupContent("Error " + data);
  })
  wustopia.marker[id].disablePermanentHighlight();
}

var show_countdown = function(id, seconds) {
  wustopia.marker[id].setPopupContent(get_time_as_string(seconds));
  if(seconds-- > 0)
  {
    setTimeout(function() {
      show_countdown(id,seconds);
    }, 1000);
  }
  else {
    wustopia.marker[id].setPopupContent("gebaut");
    get_places();
  }
}

var build = function(id) {
  $.get("/build", {
    'place': id
  }, function(data) {
    if (data == "success")
    {
      show_countdown(id, wustopia.marker[id].place.buildtime);
      wustopia.marker[id]._popup.options.closeOnClick = false;
      wustopia.marker[id]._popup.options.autoClose = false;
      wustopia.marker[id].openPopup();
    }
    else wustopia.marker[id].setPopupContent("Error " + data);
    update_resources();

  })
}

//var addItem = function(ilat, ilon, name, level, id, category, categoryid, costs)
var addItem = function(item) {
  var text = "";
  text = item.name + '<br><input type=\"button\" value=\"bauen\" onclick=\"build(' + item.id + ')\">';
  text = text + '<br>' + item.category;
  item.costs.forEach(function(item) {
    text = text + '<br>' + item.amount + " " + item.name;
  });
  if(item.buildtime) {
    text = text + "<br>Bauzeit: " + get_time_as_string(item.buildtime);
  }

  //remove old marker/layer
  if(wustopia.marker[item.id])
    wustopia.map.removeLayer(wustopia.marker[item.id]);
  wustopia.marker[item.id] = L.marker([item.lat, item.lon], {
      icon: wustopia.markerIcon[item.categoryid]
    })
    .bindPopup(text)
    .bindTooltip(item.level, {
      permanent: true
    })
    .addTo(wustopia.map)
    .on('click', earn);
  wustopia.marker[item.id].place = []
  wustopia.marker[item.id].place.id = item.id;
  wustopia.marker[item.id].place.category = item.category;
  wustopia.marker[item.id].place.level = item.level;
  wustopia.marker[item.id].place.buildtime = item.buildtime;
  if (item.collectable >= 0)
    setTimeout(function() {
      wustopia.marker[item.id].enablePermanentHighlight();
    }, item.collectable * 1000);

  //show countdown if not ready
  ready_delta = item.ready - Math.floor(Date.now() / 1000);
  if(ready_delta > 0) {
    show_countdown(item.id, ready_delta);
    wustopia.marker[item.id]._popup.options.closeOnClick = false;
    wustopia.marker[item.id]._popup.options.autoClose = false;
    wustopia.marker[item.id].openPopup();
  }

}

var scaleMap = function() {
  $("#map").css('height', $(window).height() - 30 + 'px');
};

$(window).resize(scaleMap);

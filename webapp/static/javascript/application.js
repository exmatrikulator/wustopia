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
  },
  toastr: [],
  collect_all: false
};

var gt = new Gettext({
  domain: 'wustopia'
});
var gettext = function(msgid) {
  return gt.gettext(msgid);
};

var get_time_as_string = function(time) {
  if (parseInt(time) <= 0 || isNaN(time))
    return;

  var output = "";
  var hours = Math.floor(time / 3600);
  var minutes = Math.floor((time - (hours * 3600)) / 60);
  var seconds = time - (hours * 3600) - (minutes * 60);
  if (hours > 0)
    output += hours + "h ";
  if (minutes > 0)
    output += minutes + "m ";
  if (hours == 0)
    output += seconds + "s";
  return output.trim();
}

//only for testing
var test_time = function() {
  if (
    get_time_as_string(-1) == undefined &&
    get_time_as_string() == undefined &&
    get_time_as_string(0) == undefined &&
    get_time_as_string(5) == "5s" &&
    get_time_as_string(10) == "10s" &&
    get_time_as_string(60) == "1m 0s" &&
    get_time_as_string(61) == "1m 1s" &&
    get_time_as_string(130) == "2m 10s" &&
    get_time_as_string(600) == "10m 0s" &&
    get_time_as_string(3600) == "1h" &&
    get_time_as_string(3604) == "1h" &&
    get_time_as_string(3660) == "1h 1m") {
    return true;
  } else {
    return false;
  }
}

var last_update_places = 0;
var update_places = function(force=false) {
  //allow only every 5 secounds a call
  if(!force)
  {
    if (last_update_places + 5 > Math.floor(Date.now() / 1000))
      return;
    if (wustopia.map.getZoom() < 18)
      return;
  }
  last_update_places = Math.floor(Date.now() / 1000);
  var bounds = wustopia.map.getBounds();
  var lng1 = bounds.getSouthWest().lng;
  var lat1 = bounds.getSouthWest().lat;
  var lng2 = bounds.getNorthEast().lng;
  var lat2 = bounds.getNorthEast().lat;
  $.get("update_places/" + lat1 + "," + lng1 + "," + lat2 + "," + lng2, function(data) {
    if (!wustopia.update_places_jobId)
      wustopia.update_places_jobId = data;
  });
}


var check_update_places = function() {
  $.ajax({
    url: "/update_places/" + wustopia.update_places_jobId,
    statusCode: {
      200: function() {
        get_places();
      },
      202: function() {
        setTimeout(function() {
          check_update_places();
        }, 3000);
      }
    }
  });
}


function get_places() {
  if (wustopia.session.lat && wustopia.session.lat) {
    $.getJSON("/api/places", {
      lat: wustopia.session.lat,
      lon: wustopia.session.lon
    }).done(function(data) {
      wustopia.user.places = data;
      if (data.length > 0) {
        data.forEach(function(item) {
          addItem(item);
        })
      } else {
        toastr.info(gettext("#No items found.\nWe'll look for you for new items.\nIt could take some time, until you see items."),gettext("#Info"),{"closeButton": true, "timeOut": 0});
        update_places(true);
        setTimeout(function() {
          check_update_places();
        }, 10000);
      }
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

  wustopia.map.setView([wustopia.session.lat, wustopia.session.lon], zoom);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18,
    useCache: true,
    crossOrigin: true,
    cacheMaxAge: 604800000 // 7 days
  }).addTo(wustopia.map);

  L.marker([wustopia.session.lat, wustopia.session.lon], {
      icon: L.icon({
        iconUrl: ('/static/images/resources/me_32.png'),
        iconSize: [32, 32]
      })
    }).addTo(wustopia.map)
    .bindPopup(gettext("#You"))
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
      $("#res_" + item.id).append("  " + item.amount.toLocaleString());
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
  $("#collect_all").click(function() {
    collect_all();
  });
  update_places();
});

var collect_all = function() {
  if(!wustopia.collect_all)
    return;
  $.get("/collect_all", {}, function(data) {
    $("#audio_earn").trigger('play');
    update_resources();
    get_places();
    wustopia.marker.forEach(function(marker) {
      marker.disablePermanentHighlight();
    });
    wustopia.collect_all=false;
  }).fail(function(data) {
    $("#audio_error").trigger('play');
    toastr.error(data.responseText);
  })
}

var earn = function(el) {
  //switch between marker and direct item
  var item;
  if (el.target) {
    item = el.target
  } else {
    item = el
  }
  //only if is collectable
  if (!item.place.collectable) {
    return;
  }

  var id = item.place.id;
  $.get("/earn/"+id, {}, function(data) {
    $("#audio_earn").trigger('play');
    item.place.collectable = false;
    update_resources();
  }).fail(function(data) {
    $("#audio_error").trigger('play');
    toastr.error(data.responseText);
  }).always(function() {
    wustopia.marker[id].disablePermanentHighlight();
  });

}

var show_buildtime = function(itemId) {
  //if toast is already shown
  if(wustopia.toastr[itemId])
    return

  if (wustopia.marker[itemId].place.readyin !== undefined)
    timeout = wustopia.marker[itemId].place.readyin * 1000;
  else
    timeout = wustopia.marker[itemId].place.buildtime * 1000;
  toastr.info( wustopia.marker[itemId].name, gettext("#Build") + " " + wustopia.marker[itemId].place.category , {"timeOut": timeout, "extendedTimeOut":timeout, "progressBar": true})
  wustopia.toastr[itemId] = true;
  setTimeout(function () {
    toastr.success( wustopia.marker[itemId].name, gettext("#Built") )
    wustopia.toastr[itemId] = false;
    get_places();
  }, timeout );
}


var build = function(id) {
  $.get("/build", {
    'place': id
  }, function(data) {
    $("#audio_build").trigger('play');
    $("#"+id+"build").prop("disabled",true);
    show_buildtime(id);
  }).fail(function(data) {
    $("#audio_error").trigger('play');
    toastr.error(data.responseText);
  }).always(function() {
    update_resources();
  });
}

//var addItem = function(ilat, ilon, name, level, id, category, categoryid, costs)
var addItem = function(item) {
  var text = item.name;
  text = text + "<br>" + item.category;
  item.costs.forEach(function(item) {
    text = text + "<br> <img src=\"" + item.image + "\" alt=\"" + item.name + "\"> " + item.amount;
  });
  if (item.buildtime) {
    text = text + "<br>" + gettext("#build time") + ": " + get_time_as_string(item.buildtime);
  }
  if (get_time_as_string(item.collectablein)) {
    text = text + "<br>" + gettext("#collectable in") + ": " + get_time_as_string(item.collectablein);
  }
  text = text + "<br><button id=\""+item.id+"build\" class=\"button is-primary\" onclick=\"build(" + item.id + ")\">" + gettext("#build") + "</button>";
  text = text + "<br><a href=\"/help/building/" + item.categoryid + "-" + item.category.replace(' ', '_') + "\">" + gettext("#Help") + "</a>"

  //remove old marker/layer
  if (wustopia.marker[item.id])
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
  wustopia.marker[item.id].name = item.name;
  wustopia.marker[item.id].place = [];
  wustopia.marker[item.id].place.id = item.id;
  wustopia.marker[item.id].place.category = item.category;
  wustopia.marker[item.id].place.level = item.level;
  wustopia.marker[item.id].place.buildtime = item.buildtime;
  wustopia.marker[item.id].place.ready = item.ready;
  wustopia.marker[item.id].place.collectable = false;
  if (item.collectablein >= 0)
    setTimeout(function() {
      wustopia.marker[item.id].place.collectable = true;
      wustopia.marker[item.id].enablePermanentHighlight();
      wustopia.collect_all=true;
    }, item.collectablein * 1000);

  //show countdown if not ready
  ready_delta = item.ready - Math.floor(Date.now() / 1000);
  if (ready_delta > 0) {
    wustopia.marker[item.id].place.readyin = ready_delta;
    show_buildtime(item.id);
  }

}

var scaleMap = function() {
  $("#map").css('height', $(window).height() - 30 + 'px');
};

$.getJSON("/api/markerIcon", {}).done(function(data) {
  data.forEach(function(item) {
    wustopia.markerIcon[item.id] = L.AwesomeMarkers.icon(item);
  })
});

$(window).resize(scaleMap);



var map =  L.map('map');
var lat = null;
var lon = null;
var acc = null;
var marker = new Array();

var is_update_places=false;
var update_places = function()
{
	if(is_update_places)
		return;
	is_update_places=true;
	var bounds = map.getBounds();
	var lng1 = bounds._southWest.lng;
	var lat1 = bounds._southWest.lat;
	var lng2 = bounds._northEast.lng;
	var lat2 = bounds._northEast.lat;
	$.get( "update_places/"+lat1+","+lng1+","+lat2+","+lng2, function( data ) {
		is_update_places=false;
	});
}

var init = function (position)
{
	lat = position.coords.latitude;
	lon = position.coords.longitude;
	acc = position.coords.accuracy;
	zoom = Math.round( 18 - Math.log( position.coords.accuracy ) / 10 );
	map.setView([lat, lon], zoom) ;
	L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
	}).addTo(map);

	L.marker([lat, lon], {icon:  L.icon({ iconUrl: ('http://upload.wikimedia.org/wikipedia/commons/c/cb/Icon_person_abstract_blue.jpg'), iconSize: [40, 40] }) }).addTo(map)
	.bindPopup('You, ' + user )
	.openPopup();
	ckeckItem();

	map.on("move",update_places);
}


$( document ).ready(function() {

	if (navigator.geolocation)
	{
		navigator.geolocation.getCurrentPosition(init);
		$("#user").text( user );
		$.get("/resources",{}, function(data) {
			$("#resources").html(data);
		})
	}
});

var build = function(id)
{
	$.get("/build",{'place': id}, function(data) {
		if(data == "success") marker[id].setPopupContent("gebaut");
		else marker[id].setPopupContent("Error " + data);
	})
}

var addItem = function(ilat, ilon, name, level, id, category)
{
	var text = "";
	var latlng = new L.LatLng( ilat, ilon );
	var latlng2 = new L.LatLng( lat , lon );
	if( latlng.distanceTo( latlng2 ) < 50000)
	{
		text = name + '<br><input type=\"button\" value=\"bauen\" onclick=\"build(' + id + ')\">';
	}
	else
	{
		text = name;
	}
	text = text + ' (' + Math.round(latlng.distanceTo( latlng2 ) ) + 'm)<br>Level ' + level;
	text = text + '<br>' + category;

	marker[id] = L.marker([ilat, ilon],
		{icon: L.icon({
			iconUrl: ('http://upload.wikimedia.org/wikipedia/commons/f/ff/Crystal_Clear_app_ksokoban_blue.png'),
			iconSize: [25, 25]}) })
		.bindPopup( text )
		.addTo(map);
}

var scaleMap = function()
{
	$("#map").css('height', $(window).height() - 30 + 'px');
};

$(window).resize(scaleMap);
scaleMap();

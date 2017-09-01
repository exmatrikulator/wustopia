

var map =  L.map('map');
var lat = null;
var lon = null;
var acc = null;
var marker = new Array();
var user = '';

var is_update_places=false;
var update_places = function()
{
	if(is_update_places)
		return;
	if(map.getZoom()<17)
		return;
	is_update_places=true;
	var bounds = map.getBounds();
	var lng1 = bounds.getSouthWest().lng;
	var lat1 = bounds.getSouthWest().lat;
	var lng2 = bounds.getNorthEast().lng;
	var lat2 = bounds.getNorthEast().lat;
	$.get( "update_places/"+lat1+","+lng1+","+lat2+","+lng2, function( data ) {
		is_update_places=false;
	});
}

var init = function (position)
{
	if(position.coords)
	{
		lat = position.coords.latitude;
		lon = position.coords.longitude;
		acc = position.coords.accuracy;
		zoom = Math.round( 18 - Math.log( acc ) / 10 );
	}
	else
	{
		lat="";
		lon="";
		zoom=2;
	}

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

function show_resources()
{
	$.get("/resources",{}, function(data) {
		$("#resources").html(data);
	});
}

$( document ).ready(function() {

	if (navigator.geolocation)
	{
		navigator.geolocation.getCurrentPosition(init,init);
		$("#user").text( user );
		show_resources();
	}
});

var earn = function(el)
{
	//do not collect non buildings
	if(el.target.place.level == 0)
	{
		return;
	}

	id = el.target.place.id;
	$.get("/earn",{'place': id}, function(data) {
		if(data == "success") show_resources();
		else if(data != "") marker[id].setPopupContent("Error " + data);
	})
}

var build = function(id)
{
	$.get("/build",{'place': id}, function(data) {
		if(data == "success") marker[id].setPopupContent("gebaut");
		else marker[id].setPopupContent("Error " + data);
		show_resources();
	})
}

var addItem = function(ilat, ilon, name, level, id, category, categoryid, costs)
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
	text = text + '<br>' + costs;

	marker[id] = L.marker([ilat, ilon],
		{icon: markerIcon[categoryid] })
		.bindPopup( text )
		.bindTooltip( level, {permanent:true})
		.addTo(map)
		.on('click',earn);
	marker[id].place = []
	marker[id].place.id = id;
	marker[id].place.category = category;
	marker[id].place.level = level;
}

var scaleMap = function()
{
	$("#map").css('height', $(window).height() - 30 + 'px');
};

$(window).resize(scaleMap);
scaleMap();

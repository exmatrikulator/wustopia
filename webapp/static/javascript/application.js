

var map =  L.map('map');
var lat = null;
var lon = null;
var acc = null;
var marker = new Array();

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
}

var init2 = function (position)
{
	lat = 51.245;
	lon = 7.134;
	//map = L.map('map').setView([lat, lon], 13);
	map.setView([lat, lon], 13);
	L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
	}).addTo(map);
	ckeckItem();
}

if (navigator.geolocation)
{
	navigator.geolocation.getCurrentPosition(init, init2);
	$("#user").text( user );
	$.get("/resources",{}, function(data) {
		$("#resources").html(data);
	})
}

var build = function(id)
{
	$.get("/build",{'id': id, 'user' : user}, function(data) {
		if(data == "success") marker[id].setPopupContent("gebaut");
		else marker[id].setPopupContent("Error " + data);
	})
}

var addItem = function(ilat, ilon, name, user, id, category)
{
	var text = "";
	var latlng = new L.LatLng( ilat, ilon );
	var latlng2 = new L.LatLng( lat , lon );
	if( latlng.distanceTo( latlng2 ) < 20)
	{
		text = name + '<br><input type=\"button\" value=\"bauen\" onclick=\"build(' + id + ')\">';
	}
	else
	{
		text = name;
	}
	text = text + ' (' + Math.round(latlng.distanceTo( latlng2 ) ) + 'm)<br>owned by ' + user;
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



var map = null;
var lat = null;
var lon = null;
var acc = null;
var marker = new Array();
var user = '';
var wustopia = {user:{built:[], resources:[]}};

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

	$.getJSON( "/api/places", { lat:lat,  lon:lon }).done( function(data) {
		wustopia.user.built = data;
		data.forEach(function(item) {
			addItem(item);
		})
	});


	map.setView([lat, lon], zoom) ;
	L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
	}).addTo(map);

	L.marker([lat, lon], {icon:  L.icon({ iconUrl: ('http://upload.wikimedia.org/wikipedia/commons/c/cb/Icon_person_abstract_blue.jpg'), iconSize: [40, 40] }) }).addTo(map)
	.bindPopup('You, ' + user )
	.openPopup();

	map.on("move",update_places);
}


function update_resources()
{

	$.getJSON( "/api/resources" ).done( function(data) {
		wustopia.user.resources = data;
		$("#resources").html("");
		data.forEach(function(item) {
			if(item.major)
			{
				resclass = "resource";
			}
			else
			{
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
			$("#res_" + item.id).append( "  " + item.amount );
		})
	});
}

$( document ).ready(function() {
	map =  L.map('map');
	scaleMap();
	if (navigator.geolocation)
	{
		navigator.geolocation.getCurrentPosition(init,init);
		$("#user").text( user );
		update_resources();
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
		if(data == "success") update_resources();
		else if(data != "") marker[id].setPopupContent("Error " + data);
	})
	marker[id].disablePermanentHighlight();
}

var build = function(id)
{
	$.get("/build",{'place': id}, function(data) {
		if(data == "success") marker[id].setPopupContent("gebaut");
		else marker[id].setPopupContent("Error " + data);
		update_resources();
	})
}

//var addItem = function(ilat, ilon, name, level, id, category, categoryid, costs)
var addItem = function(item)
{
	var text = "";
	text = item.name + '<br><input type=\"button\" value=\"bauen\" onclick=\"build(' + item.id + ')\">';
	text = text + '<br>Level ' + item.level;
	text = text + '<br>' + item.category;
	text = text + '<br>' + item.costs;

	marker[item.id] = L.marker([item.lat, item.lon],
		{icon: markerIcon[item.categoryid] })
		.bindPopup( text )
		.bindTooltip( item.level, {permanent:true})
		.addTo(map)
		.on('click',earn);
	marker[item.id].place = []
	marker[item.id].place.id = item.id;
	marker[item.id].place.category = item.category;
	marker[item.id].place.level = item.level;
	if(item.collectable >= 0)
		setTimeout(function(){ marker[item.id].enablePermanentHighlight(); }, item.collectable * 1000);
}

var scaleMap = function()
{
	$("#map").css('height', $(window).height() - 30 + 'px');
};

$(window).resize(scaleMap);

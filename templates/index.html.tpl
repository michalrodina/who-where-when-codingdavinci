<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{site.title}} | Kdo? Kdy? Kde?</title>
    <script type="text/javascript" src="js/OpenLayers/OpenLayers.js"></script>
    <link type="text/css" rel="stylesheet" href="styles/main.css" />
</head>
<body>
<div id="header"></div>
<div id="map-container">
<div id="map"></div>
</div>
<div id="footer"></div>
<script type="text/javascript">
map = new OpenLayers.Map("map");
var fromProjection = new OpenLayers.Projection("EPSG:4326");   // Transform from WGS 1984
var toProjection   = new OpenLayers.Projection("EPSG:900913"); // to Spherical Mercator Projection

map.addLayer(new OpenLayers.Layer.OSM());
map.setCenter(new OpenLayers.LonLat({{map.center_lon}}, {{map.center_lat}}).transform( fromProjection, toProjection), {{map.zoom}})

var markers = new OpenLayers.Layer.Markers( "Markers" );
map.addLayer(markers);

var size = new OpenLayers.Size(21,25);
var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
var icon = new OpenLayers.Icon('js/OpenLayers/marker.png', size, offset);


const xhttp = new XMLHttpRequest();
  xhttp.onload = function() {
        var json = JSON.parse(this.responseText);
        for(i=0; i<json.data.length; i++) {
            if(json.data[i].marker) {
                console.log(json.data[i], 'marker', json.data[i].marker[1], json.data[i].marker[0]);
                var marker = new OpenLayers.Marker(new OpenLayers.LonLat(json.data[i].marker[0], json.data[i].marker[1]).transform( fromProjection, toProjection), icon.clone());
                marker.dummy = json.data[i].name + "<br>\n" + json.data[i].birthDate + " (" + json.data[i].birthPlace+") - " + json.data[i].deathDate + " (" + json.data[i].deathPlace +")";
                //here add mouseover event
                marker.events.register('mouseover', marker, function(evt) {
                    popup = new OpenLayers.Popup.FramedCloud("Popup",
                        this.lonlat,
                        null,
                        '<div style="background: white;">'+this.dummy+'</div>',
                        null,
                        false);
                    map.addPopup(popup);
                });
                //here add mouseout event
                marker.events.register('mouseout', marker, function(evt) {popup.hide();});

                markers.addMarker(marker);
            }

        }

    }
  xhttp.open("GET", "data/markers", true);
  xhttp.send();

</script>
</body>
</html>
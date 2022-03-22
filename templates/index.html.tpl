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
</script>
</body>
</html>
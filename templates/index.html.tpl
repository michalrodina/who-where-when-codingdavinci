<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{site.title}} | Kdo? Kdy? Kde?</title>
    <script type="text/javascript" src="js/ol/ol.js"></script>
    <link type="text/css" rel="stylesheet" href="js/ol/ol.css" />
    <script type="text/javascript" src="js/main.js"></script>
    <link type="text/css" rel="stylesheet" href="styles/main.css" />
</head>
<body>
<div id="header"></div>
<div id="map-container">
<div id="map"></div>
<div id="popup" class="ol-popup">
     <a href="#" id="popup-closer" class="ol-popup-closer"></a>
     <div id="popup-content"></div>
 </div>
</div>
<div id="footer"></div>

<script type="text/javascript">
ol.proj.useGeographic();

var map = new ol.Map({
      layers: [
        new ol.layer.Tile({
          source: new ol.source.OSM(),
        }),
      ],
      target: 'map',
      view: new ol.View({
        center: [{{map.center_lon}}, {{map.center_lat}}],
        zoom: {{map.zoom}},
      }),
    });

markers_source = new ol.source.Vector({
    features: []
});

var icon_style = new ol.style.Style({
  image: new ol.style.Icon(({
    anchor: [0.5, 46],
    //size: [15, 45],
    scale: 0.1,
    anchorXUnits: 'fraction',
    anchorYUnits: 'pixels',
    opacity: 0.75,
    src: 'styles/img/marker.png'
  }))
});

var markers_layer = new ol.layer.Vector({
    source: markers_source
});

map.addLayer(markers_layer);

const xhttp = new XMLHttpRequest();
xhttp.onload = function() {
    var json = JSON.parse(this.responseText);
    for(i=0; i<json.data.length; i++) {
        if(json.data[i].marker) {
            var marker = new ol.Feature({
                geometry: new ol.geom.Point([json.data[i].marker[0], json.data[i].marker[1]]),
                data: json.data[i].name + "<br>\n" + json.data[i].birthDate + " (" + json.data[i].birthPlace+") - " + json.data[i].deathDate + " (" + json.data[i].deathPlace +")"
            });
            marker.setStyle(icon_style);
            markers_source.addFeature(marker);
        }
    }
}
xhttp.open("GET", "data/markers", true);
xhttp.send();

var container = document.getElementById('popup');
var content = document.getElementById('popup-content');
var closer = document.getElementById('popup-closer');

var overlay = new ol.Overlay({
    element: container,
    autoPan: true,
    autoPanAnimation: {
        duration: 250
    }
});
console.log(overlay);
map.addOverlay(overlay);

closer.onclick = function() {
    overlay.setPosition(undefined);
    closer.blur();
    return false;
};

map.on('singleclick', function (event) {
    if (map.hasFeatureAtPixel(event.pixel) === true) {
        var coordinate = event.coordinate;
        content.innerHTML = '';
        map.forEachFeatureAtPixel(event.pixel, function(feature, one) {
            content.innerHTML += feature.A.data + '<br>\n<br>\n';
        })

        overlay.setPosition(coordinate);
    } else {
        overlay.setPosition(undefined);
        closer.blur();
    }
});
</script>
</body>
</html>
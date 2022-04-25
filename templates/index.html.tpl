<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{site.title}} | Kdo? Kdy? Kde?</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
    <script type="text/javascript" src="js/ol/ol.js"></script>
    <link type="text/css" rel="stylesheet" href="js/ol/ol.css" />
    <script type="text/javascript" src="js/main.js"></script>
    <link type="text/css" rel="stylesheet" href="styles/main.css" />
</head>
<body>
<div id="header"><a id="main-logo"><img src="styles/img/logo.png" height="8w5"/></a></div>
<div id="map-container">
<div id="map"></div>
    <div id="marker-popup" class="ol-popup">
         <a href="#" id="marker-popup-closer" class="ol-popup-closer"></a>
         <div id="marker-popup-content"></div>
    </div>
</div>
</div>
<div id="filters" class="content-box">
    <a href="#" id="filters-closer" class="content-closer"></a>
    <form id="filter-form">
    <label for="filter-okres">Okres</label>
    <select name="filter-okres" id="filter-okres">
    {% for each in okresy %}

    <option value="{{each.id}}" {% if each == "list_status" %} selected {% endif %}>{{each.name}}</option>

    {% endfor %}
    </select>
    <button id="filters-submit">Filtrovat</button>
</div>
<div id="content" class="content-box">
<a href="#" id="content-closer" class="content-closer"></a>
<div class="content-wrap">
</div>
</div>
<div id="footer"></div>

<script type="text/javascript">
$(function() {

    console.log('Hello!');

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

    var icon_style = new ol.style.Style({
      image: new ol.style.Icon(({
        anchor: [0.5, 0.5],
        size: [278, 278],
        scale: 0.2,
        anchorXUnits: 'fraction',
        anchorYUnits: 'fraction',
        opacity: 0.75,
        src: 'styles/img/spendlik1.png'
      }))
    });

    var label_style = new ol.style.Style({
      text: new ol.style.Text({
        font: '12px Calibri,sans-serif',
        overflow: true,
        fill: new ol.style.Fill({
          color: '#000'
        }),
        stroke: new ol.style.Stroke({
          color: '#fff',
          width: 3
        }),
        offsetY: 0
      })
    });

    markers_source = new ol.source.Vector({
        features: []
    });

    var markers_layer = new ol.layer.Vector({
        source: markers_source,
        style: function(feature) {
            console.log(feature);
            label_style.getText().setText(feature.get('name'));
            return feature.A.style;
        }
    });

    $('#filter-form').on('submit', function(e) {
        e.preventDefault();

        var data_filter = {
            "okres": $('#filter-form #filter-okres').val()
        };
        console.log(data_filter);
        load_markers(data_filter);

    });

    function load_markers(data_filter) {

        const xhttp = new XMLHttpRequest();
        xhttp.onload = function() {

            markers_source.clear();

            var json = JSON.parse(this.responseText);
            for(i=0; i<json.data.length; i++) {
                if(json.data[i].marker) {
                    var marker_data = json.data[i].data
                    //console.log(marker_data);
                    text = "<h2>"+marker_data[0].location.replace('--', ', okres ')+"</h2>\n";

                    for(j=0; j<marker_data.length; j++) {
                        //console.log(marker_data[j]);
                        //console.log(marker_data[j].name);
                        var id = marker_data[j].s.substring(32);
                        text += '<h3><a href="http://127.0.0.1:8080/data/item/'+id+'" class="content-link-person" data-key="'+id+'">'+marker_data[j].name+"</a></h3>\n";
                        text += '<p>'+marker_data[j].description+"</p><br>\n";
                        text += "<br>\n";
                    }
                    var marker = new ol.Feature({
                        geometry: new ol.geom.Point([json.data[i].marker[0], json.data[i].marker[1]]),
                        //data: json.data[i].name + "<br>\n" + json.data[i].birthDate + " (" + json.data[i].birthPlace+") - " + json.data[i].deathDate + " (" + json.data[i].deathPlace +")"
                        data: text,
                        name: ''+marker_data.length,
                        style: [icon_style, label_style]
                    });

                    markers_source.addFeature(marker);
                }
            }

            map.addLayer(markers_layer);
        }

        xhttp.open("POST", "data/markers", true);
        xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        console.log(data_filter);
        xhttp.send($.param(data_filter));

    }



    var container = document.getElementById('marker-popup');
    var content = document.getElementById('marker-popup-content');
    var closer = document.getElementById('marker-popup-closer');

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


    var content_box = document.getElementById('content');

    map.on('singleclick', function (event) {
        if (map.hasFeatureAtPixel(event.pixel) === true) {
            var coordinate = event.coordinate;
            content_box.innerHTML = '';
            map.forEachFeatureAtPixel(event.pixel, function(feature, one) {
                content_box.innerHTML += feature.A.data + '<br>\n<br>\n';
            })

            // overlay.setPosition(coordinate);
            //overlay.setPosition(undefined);
            //closer.blur();
            $(content_box).show(100);
        } else {
            $(content_box).blur().hide(100);
            //overlay.setPosition(undefined);
            //closer.blur();
        }
    });

    load_markers({"okres": "Plzeň"});
});
</script>
</body>
</html>
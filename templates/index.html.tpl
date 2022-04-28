<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{site.title}} | Osobnosti plzeňského kraje</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
    <script type="text/javascript" src="js/ol/ol.js"></script>
    <link type="text/css" rel="stylesheet" href="js/ol/ol.css" />
    <script type="text/javascript" src="js/main.js"></script>
    <link type="text/css" rel="stylesheet" href="styles/main.css" />
</head>
<body>
<div id="header"><a id="main-logo"><img src="styles/img/logo.png" height="85"/></a><h1>Osobnosti plzeňského kraje</h1></div>
<div id="map-container">
<div id="map"></div>
    <div id="marker-popup" class="ol-popup">
         <a href="#" id="marker-popup-closer" class="ol-popup-closer"></a>
         <div id="marker-popup-content"></div>
    </div>
</div>
</div>
<div id="filters" class="content-box">
    <a href="#" id="filters-closer" class="content-closer open">&gt;</a>
    <div class="content-wrap">
    <h2>Výběr osobností</h2>
    <form id="filter-form">
    <div class="filter-field">
        <!-- <label for="filter-okres">Okres</label> -->
        <select name="filter-okres" id="filter-okres">
            <option value="">okres</option>
            {% for each in okresy %}

            <option value="{{each.id}}" {% if default_filter.okres == each.id %} selected {% endif %} >{{each.name}}</option>

            {% endfor %}
        </select>
    </div>

    <div class="filter-field">
        <!-- <label for="filter-obec">Obec</label> -->
        <select name="filter-obec" id="filter-obec">
            <option value="">obec</option>
            {% for each in obce %}

            <option value="{{each.id}}" {% if default_filter.filter == "obec" and each == default_filter.value %} selected {% endif %}>{{each.name}}</option>

            {% endfor %}
        </select>
    </div>

    <div class="filter-field">
        <!-- <label for="filter-obor">Obor</label> -->
        <select name="filter-obor" id="filter-obor">
            <option value="">obor</option>
            {% for each in obory %}

            <option value="{{each.id}}" {% if default_filter.filter == "obor" and each == default_filter.value %} selected {% endif %}>{{each.name}}</option>

            {% endfor %}
        </select>
    </div>

    <div class="filter-field">
        <!-- <label for="filter-obor">Obor</label> -->
        <input type=="text" name="filter-fulltext" id="filter-fulltext" placeholder="jméno"/>
    </div>
    <button id="filters-submit">Filtrovat</button>
    </div>
</div>
<div id="content" class="content-box">
<a href="#" id="content-closer" class="content-closer">&gt;</a>
<div class="content-wrap">
</div>
</div>
<div id="footer"></div>

<script type="text/javascript">
$(function() {

    $('.content-closer').on('click', function(e) {
        e.preventDefault();
        var open = $(this).is('.open');
        if(open) {
            $(this).parent().animate({"width": "0px"}, 250);
            $(this).siblings('.content-wrap').hide();
            $(this).removeClass('open').addClass('closed');
            $(this).html('&lt;');

        } else {
            $(this).parent().animate({"width": "50%"}, 250);
            $(this).siblings('.content-wrap').show();
            $(this).removeClass('closed').addClass('open');
            $(this).html('&gt;');


        }

        console.log('content-closer', open);

        return false;

    });


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

    setTimeout(function() {
        map.updateSize();
    }, 100);

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
            // console.log(feature);
            label_style.getText().setText(feature.get('name'));
            return feature.A.style;
        }
    });

    $('#filter-form').on('submit', function(e) {
        e.preventDefault();

        var data_filter = {

        };

        if($('#filter-form #filter-okres').val() != "") {
            data_filter["okres"] = $('#filter-form #filter-okres').val();
        }
        if($('#filter-form #filter-obec').val() != "") {
            data_filter["obec"] = $('#filter-form #filter-obec').val();
        }
        if($('#filter-form #filter-obor').val() != "") {
            data_filter["obor"] = $('#filter-form #filter-obor').val();
        }
        if($('#filter-form #filter-fulltext').val() != "") {
            data_filter["fulltext"] = $('#filter-form #filter-fulltext').val();
        }

        load_markers(data_filter);

        load_obce(data_filter);




    });

    $('#filter-form #filter-okres').on('change', function() {
        data_filter = {"okres": $(this).val()};

        $('#filter-form #filter-obce').attr('disabled', 'disabled');
        load_obce(data_filter);
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
                    var person_rows = $('<div />');
                    $(person_rows).append($("<h2>"+marker_data[0].location.replace('--', ', ')+"</h2>\n"));

                    for(j=0; j<marker_data.length; j++) {
                        //console.log(marker_data[j]);
                        //console.log(marker_data[j].name);
                        var id = marker_data[j].s.substring(32);
                        var text = "";

                        var person = $('<div class="person"/>');
                        person.append(
                            $('<h3>').append(
                                $('<a href="#" data-id="'+id+'"/>').html(marker_data[j].name)
                            )
                        );
                        text += '<h3><a href="http://127.0.0.1:8080/data/item/'+id+'" class="content-link-person" data-key="'+id+'">'+marker_data[j].name+"</a></h3>\n";
                        text += '<p><span class="date brith-date">'+marker_data[j].birthDate + '</span> - <span class="date death-date">' + marker_data[j].deathDate + "</span></p><br>\n";
                        text += '<p>' + marker_data[j].subjects + "</p><br>\n";
                        text += "<br>\n";
                        $(person_rows).append(person);
                    }
                    var marker = new ol.Feature({
                        geometry: new ol.geom.Point([json.data[i].marker[0], json.data[i].marker[1]]),
                        data: person_rows.html(),
                        name: ''+marker_data.length,
                        style: [icon_style, label_style]
                    });

                    markers_source.addFeature(marker);
                }
            }

            map.addLayer(markers_layer);

            var layerExtent = markers_source.getExtent();
            console.log(layerExtent);
            if (layerExtent) {
                map.getView().fit(layerExtent);
            }

        }

        xhttp.open("POST", "data/markers", true);
        xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        console.log(data_filter);
        xhttp.send($.param(data_filter));

    }

    function load_obce(data_filter) {
        // reload filters
        const xhttp = new XMLHttpRequest();
        xhttp.onload = function() {

            var json = JSON.parse(this.responseText);
            console.log('reload filters', json['data']);
            $('#filter-form #filter-obec').html('<option value="">obec</option>');

            for(var i=1; i<json['data'].length; i++) {
                console.log(json['data'][i]);
                var opt = $('<option value="'+json['data'][i]['id']+'">'+json['data'][i]['name']+'</option>');
                if(json['data'][i]['id'] == data_filter['obec']) {
                    $(opt).attr('selected', 'selected');
                }
                $('#filter-form #filter-obec').append(opt);
            }

            $('#filter-form #filter-obce').removeAttr('disabled');
        }

        xhttp.open("POST", "data/obce", true);
        xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        xhttp.send($.param(data_filter));

    }

    function load_detail(person_id) {


        const xhttp = new XMLHttpRequest();
        xhttp.onload = function() {

            var content_html = $('<div class="content-html">');
            var json = JSON.parse(this.responseText);


            var name = $('<h2 />');
            $(name).html(json['data']['name']);
            $(content_html).append(name);
            //*†
            var life = $('<div class="content-life-span"/>');
            $(life).append($('<span class="birth-date">'+json['data']['birthDate']+' '+json['data']['birthPlace'].replace('--', ', ')+'</span>'));
            if(typeof json['data']['deathDate'] !== 'undefined' || typeof json['data']['deathPlace'] !== 'undefined') {
                $(life).append($('<br />'));
                var deathText = '';
                if(typeof json['data']['deathDate'] !== 'undefined') {
                    deathText += json['data']['deathDate'];
                } else {
                    deathText += '????-??-??';
                }

                if(typeof json['data']['deathPlace'] !== 'undefined') {
                    deathText += ' '+json['data']['deathPlace'].replace('--', ', ');
                } else {
                    deathText += ' ???';
                }

                $(life).append($('<span class="death-date">'+deathText+'</span>'));
            }

            var desc = $('<div class="content-description" /><h3>Biografie</h3>');
            var desc_p = $('<p>'+json['data']['description']+'</p>');
            $(desc).append(desc_p);

            var image = $('<img class="content-portrait" width="150"/>');
            if(typeof json['data']['image'] !== 'undefined' && json['data']['image'] != false) {
                $(image).attr('src', json['data']['image']);
            } else {
                $(image).attr('src', 'styles/img/portret.png');
            }

            var sources = $('<div class="content-sources" /><h3>Zdroje</h3>');
            var sources_list = $('<ul />');
            var src = json['data']['sources'].split(';');
            console.log(src);
            for(var i=0; i<src.length; i++) {
                $(sources_list).append($('<li>'+src[i]+'</li>'));

            }
            $(sources).append(sources_list);

            $(content_html).append(image);
            $(content_html).append(life);

            $(content_html).append(desc);

            $(content_html).append(sources);





            $(content_box).html($(content_html).html());

        }

        xhttp.open("GET", "data/item/"+person_id, true);
        xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        xhttp.send();

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

            $('.person').each(function(el) {
                $(this).find('a').on('click', function(e) {
                    e.preventDefault();
                    var person_id = $(e.target).attr('data-id');
                    console.log('clicked', $(this), $(e.target).attr('data-id'));
                    load_detail(person_id);
                });
            });

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

    load_markers({{default_filter}});
});
</script>
</body>
</html>
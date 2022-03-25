# # Data API Flask Blueprint
# Tento blueprint bude poskytovat rozhraní pro AJAX načítání prvků do mapy
# - Flask Blueprint umoznuje definovat routy z externich souboru,
#       ktere jsou potom jako celek zaregistrovany do korenove aplikace
#
# Bude využívat tridu SPARQLSource, ktera slouzi jako konektor do datového endpointu knihovny
# - Umisteno v modulu 'datasource'
#
# Bude vracet veskera data v JSON formatu
# - Konkretni format musime definovat

# # TODO:
# - Vyzkoumat efektivni zpusob vypisovani dat do JSONu (nejradeji pomoci render_template)
# - Definovat potrebne endpointy (markery, infoboxy, popup okna s detaily, atp.)

from flask import Blueprint, render_template, Response
from datasource import DataSource
import pandas as pd
import json

# Registrace modulu jako Flask Blueprint
data_api = Blueprint('data_api', __name__, template_folder='./templates/')

# Aktivace datoveho zdroje
sparql = DataSource()


# Dummy JSON data
@data_api.route('/data/markers')
def data_markers():
    data = sparql.load_items(False)
    df = pd.DataFrame(data)

    markers = []
    for m in df.marker.unique():
        # print(df[df.marker==m])
        markers.append({"marker": m, "data": df[df.marker==m].to_dict(orient='records')})

    r = Response(response=render_template('data_markers.json.tpl', data=json.dumps(markers)))
    r.headers["Content-Type"] = "application/json; charset=utf-8"
    return r
    pass


@data_api.route('/data/subjects')
def data_subjects():
    data = sparql.load_subjects()

    r = Response(response=render_template('data_markers.json.tpl', data=json.dumps(data)))
    r.headers["Content-Type"] = "application/json; charset=utf-8"
    return r


@data_api.route('/data/item/<param>')
def data_item(param):
    # Ocekavane polozky:
    # - Jmeno           (<http://schema.org/name)
    # - Obory           (<http://purl.org/dc/terms/subjects>)
    # - Narozeni datum  (<http://schema.org/birthDate>)
    # - Narozeni misto  (<http://schema.org/birthPlace>)
    # - Umrti datum     (<http://schema.org/deathDate>)
    # - Umrti misto     (<http://schema.org/deathPlace>)
    # - Popis           (<http://schema.org/description>)
    # - Zamestnani      (<http://schema.org/hasOccupation>)
    # - Zdroje          (<http://www.loc.gov/mads/rdf/v1#Source>)
    data = sparql.load_item(param)

    return render_template('data_markers.json.tpl', data=json.dumps(data))
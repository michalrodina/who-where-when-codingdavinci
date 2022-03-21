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

from flask import Blueprint, render_template
from datasource import DataSource

# Registrace modulu jako Flask Blueprint
data_api = Blueprint('data_api', __name__, template_folder='./templates/')

# Aktivace datoveho zdroje
sparql = DataSource()


# Dummy JSON data
@data_api.route('/data/markers')
def data_markers():
    data = sparql.load_data(False)

    return render_template('data_markers.json.tpl', data=data)
    pass

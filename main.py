# Main soubor aplikace
# Definice a spusteni flask serveru, index router

# # TODO:
# - WSGI integrace pro produkci

from flask import Flask, render_template, send_from_directory
from dataapi import data_api
from dataapi import sparql
import json

import os
os.chdir(os.path.dirname(__file__))

# Inicializace Flask aplikace
app = Flask(__name__, template_folder='./templates/')
app.register_blueprint(data_api)

# Konfigurace pro jednotlive kiosky ulozena v JSON
config_json = open('conf/sites.json', encoding='utf8')
configs = json.load(config_json)


##
# JS router
#
# poskytuje soubory ze slozky js
@app.route('/js/<path:path>')
def file_js(path):
    return send_from_directory('js', path)


##
# CSS router
#
# poskytuje soubory ze slozky styles
@app.route('/styles/<path:path>')
def file_css(path):
    return send_from_directory('styles', path)

##
# Index router
#
# Vychozi stranka aplikace
@app.route('/', defaults={'config': 'general'})
@app.route('/<config>')
def index(config):
    # vyhledat konifguraci kiosku, pokud neexistuje pouzit general
    if config not in configs.keys():
        config = 'general'
    vars = configs[config]
    # vars['okresy'] = [{"name": "Klatovy", "id": "Klatovy"}, {"name": "Plzeň - sever", "id": "Plzeň"}]
    vars['okresy'] = sparql.load_okresy(vars['default_filter'])

    # vars['obce'] = [{"name": "Klatovy", "id": "Klatovy"}, {"name": "Tachov", "id": "Tachov"}, {"name": "Plzeň", "id": "Plzeň"}]
    vars['obce'] = sparql.load_obce(vars['default_filter'])

    # vars['obory'] = [{"name": "Keramika", "id": "keram"}, {"name": "Malba", "id": "malíř"}, {"name": "Sociologie", "id": "sociolo"}]
    vars['obory'] = [
        {"id": "astrol", "name": "Astrologie"},
        {"id": "astron", "name": "Astronomie"},
        {"id": "fyzi", "name": "Fyzika"},
        {"id": "básn", "name": "Poezie"},
        {"id": "benedikt", "name": "Benediktíni"},
        {"id": "botan", "name": "Botanika"},
        {"id": "budd", "name": "Buddhismus"},
        {"id": "šlecht", "name": "Šlechta"},
        {"id": "tane", "name": "Tanec"},
        {"id": "techni", "name": "Technika"},
        {"id": "těl", "name": "Tělesná výchova"},
        {"id": "telev", "name": "Televize"},
        {"id": "teol", "name": "Teologie"},
        {"id": "textil", "name": "Textilní průmysl"},

    ]
    # vykreslit sablonu s nactenou konfiguraci (**operator vlozi obsah dictu jako promenne)
    return render_template('index.html.tpl', **vars, markers=[])
    pass
if __name__ == "__main__":
    # Spusteni VYVOJOVEHO serveru
    app.run(host='127.0.0.1', port=8080, debug=True)

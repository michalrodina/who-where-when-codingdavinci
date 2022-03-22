# Main soubor aplikace
# Definice a spusteni flask serveru, index router

# # TODO:
# - WSGI integrace pro produkci

from flask import Flask, render_template, send_from_directory
from dataapi import data_api
import json

# Inicializace Flask aplikace
app = Flask(__name__, template_folder='./templates/')
app.register_blueprint(data_api)

config_json = open('conf/sites.json')
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
    if config not in configs.keys():
        config = 'general'

    center_lat = configs[config]['map']['center_lat']
    center_lon = configs[config]['map']['center_lon']
    zoom = configs[config]['map']['zoom']

    return render_template('index.html.tpl', center_lat=center_lat, center_lon=center_lon, zoom=zoom)
    pass


# Spusteni VYVOJOVEHO serveru
app.run(host='127.0.0.1', port=8080, debug=True, ssl_context='adhoc')

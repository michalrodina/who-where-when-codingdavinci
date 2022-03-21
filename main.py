# Main soubor aplikace
# Definice a spusteni flask serveru, index router

# # TODO:
# - WSGI integrace pro produkci

from flask import Flask, render_template
from dataapi import data_api

# Inicializace Flask aplikace
app = Flask(__name__, template_folder='./templates/')
app.register_blueprint(data_api)


##
# Index router
#
# Vychozi stranka aplikace
@app.route('/')
@app.route('/index.html')
def index():

    return render_template('index.html.tpl')
    pass


# Spusteni VYVOJOVEHO server
app.run(host='127.0.0.1', port=8080, debug=True, ssl_context='adhoc')

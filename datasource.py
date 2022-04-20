# # DataSource trida
# Tato trida bude poskytovat kompletni rozhrani mezi mistnimi endpointy a zdrojovou databazi plzenske knihovny


from SPARQLWrapper import SPARQLWrapper, JSON
import json
from collections import defaultdict
import re

# # TODO:
# - Navrhnout metody pro ziskavani dat
# - Implementovat metody:
# - - nacist vechny polozky pro mapu (moznost poslat do metody ruzne filtry) - rozpracovano (load_items)
# - - nacist jednu polozky pro zobrazni detailu (filtr podle id) - rozpracovano (load_item)
# - - nacist obory pusobnosti - rozpracovano (load_subjects)

class DataSource:

    ##
    # Konstruktor
    #
    # Vytvori (singleton?) spojeni s databazi plzenske knihovny
    def __init__(self):
        # REOS SPAQRL Endpoint
        self.reos = SPARQLWrapper('https://fuseki.lib-lab.cz/reos/sparql')
        self.reos.setReturnFormat(JSON)

        # Wikidata SPARQL Endpoint
        self.wiki = SPARQLWrapper('https://query.wikidata.org/sparql')
        self.wiki.setReturnFormat(JSON)

        self.load_geoloc()


    def load_geoloc(self, city_label=""):
        self.geoloc = {}

        self.wiki.setQuery("""
            SELECT DISTINCT ?locationLabel ?regionLabel ?geoloc WHERE {
                ?location wdt:P17 wd:Q213.
                ?location wdt:P131 ?region .
                ?location wdt:P31 wd:Q5153359 .
                ?location wdt:P625 ?geoloc .
                # cs_label pro poteby pripadne filtrace v dotazu
                #?location rdfs:label ?cs_label .
                #FILTER (lang(?cs_label) = "cs") .
                #FILTER (regex((?cs_label), "%s")).

                SERVICE wikibase:label { bd:serviceParam wikibase:language "cs". }
                }

        """ % city_label)

        try:
            data = self.wiki.queryAndConvert()

            for g in data['results']['bindings']:
                self.geoloc[g['locationLabel']['value'] + '--' + g['regionLabel']['value'].replace('okres ', '')] = \
                    g['geoloc']['value']
        except:
            print('Nepodařilo se načíst wikidata zdroj geolokace. Načítám lokální JSON zdroj.')
            fjson = open('assets/wikidata_geoloc.json', encoding='utf8')
            data = json.load(fjson) # nacist z JSONu
            for g in data:
                self.geoloc[g['locationLabel'] + '--' + g['regionLabel'].replace('okres ', '')] = \
                    g['geoloc']

        # Natahnout geolokacni data pro obce CR z Wikidat

        pass

    # Gettery:
    ##
    # Nacist obory pusobnosi
    #
    # TODO: Je v tom slusnej bordel :/
    def load_subjects(self):
        self.reos.setQuery("""
            SELECT DISTINCT ?subj
            WHERE {
                ?s <http://purl.org/dc/terms/subjects> ?subj . 
            }
        
        """)

        data = self.reos.queryAndConvert()

        ret = []
        for d in data['results']['bindings']:
            ret.append(d['subj']['value'])

        return ret

    ##
    # Load items metoda
    #
    # Nacita vsechny polozky z datasource s vybranou mnozinou vlastnosti
    def load_items(self, data_filter):
        # zpracuj data_filter

        # nacti data
        query = """
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                               
            SELECT
                ?s 
                ?name
                ?location
                (GROUP_CONCAT(?desc) AS ?description)
                ?birthDate
                ?birthPlace 
                ?deathDate
                ?deathPlace
                (GROUP_CONCAT(?subj;SEPARATOR="\\n") AS ?subjects)
            WHERE
            {{
                ?s <http://schema.org/name> ?name .
                ?s <http://schema.org/workLocation> ?location .
                ?s <http://schema.org/description> ?desc .
                ?s <http://schema.org/birthDate> ?birthDate .
                ?s <http://schema.org/birthPlace> ?birthPlace .
                OPTIONAL {{?s <http://schema.org/deathDate> ?deathDate}} .
                OPTIONAL {{?s <http://schema.org/deathPlace> ?deathPlace}} .
                ?s <http://purl.org/dc/terms/subjects> ?subj .
                #FILTER regex(?subj, "keram", "i")
                #FILTER regex(?name, "Jan","i")
                {birthDate}
            }}
            GROUP BY ?s ?name ?location ?birthPlace ?birthDate ?deathDate ?deathPlace
        """
        queryToUse = query.format(birthDate = "FILTER (?birthDate > \"1800-01-01\"^^xsd:date)")

        self.reos.setQuery(queryToUse)

        data = self.reos.queryAndConvert()

        ret = []
        for person in data['results']['bindings']:
            item = {}
            try:
                item['s'] = person['s']['value']
            except KeyError:
                item['s'] = 'Chyba'

            try:
                item['name'] = person['name']['value']
            except KeyError:
                item['name'] = 'Chyba'

            try:
                item['location'] = person['location']['value']
                #city = person['birthPlace']['value'].split('--')
                #if city[0] in self.geoloc:
                if person['location']['value'] in self.geoloc:
                    # print(city[0], city[1], self.geoloc[city[0]])
                    ##point = re.findall("\d+\.\d+",  self.geoloc[city])
                    point = re.findall("\d+\.\d+",  self.geoloc[person['location']['value']])
                    item['marker'] = (point[0], point[1])
                else:
                    # print(city[0], city[1], 'Nenalezeno')
                    item['marker'] = False
            except KeyError:
                item['location'] = '?'
                item['marker'] = False

            try:
                item['description'] = person['description']['value']

            except KeyError:
                item['description'] = '?'

            try:
                item['birthDate'] = person['birthDate']['value']

            except KeyError:
                item['birthDate'] = '?'

            try:
                item['birthPlace'] = person['birthPlace']['value']
            except KeyError:
                item['birthPlace'] = '?'

            try:
                item['deathDate'] = person['deathDate']['value']
            except KeyError:
                item['deathDate'] = '?'

            try:
                item['deathPlace'] = person['deathPlace']['value']
            except KeyError:
                item['deathPlace'] = '?'

            try:
                item['subjects'] = person['subjects']['value']
            except KeyError:
                item['subjects'] = '?'

            ret.append(item)

        return ret
        pass

    def search_name(self):

        pass

    ##
    # Nacist jednu osobu dle <https://svkpk.cz/resources/reos/{subject}>
    #
    # Data budou zobrazena v detailnim nahledu konkretni osoby
    #
    # @TODO: Nacist vsechny vlastnosti
    # @TODO: Zkusit dohledat fotku z wikidata/wikimedia?
    def load_item(self, subject):

        self.reos.setQuery("""
            SELECT
                ?s 
                ?name
                ?location
                ?description 
                ?birthDate
                ?birthPlace 
                ?deathDate
                ?deathPlace
                (GROUP_CONCAT(?subj) AS ?subjects)
            WHERE
              {
                ?s <http://schema.org/name> ?name .
                ?s <http://schema.org/workLocation> ?location .
                ?s <http://schema.org/description> ?description .
                ?s <http://schema.org/birthDate> ?birthDate .
                ?s <http://schema.org/birthPlace> ?birthPlace .
                OPTIONAL {?s <http://schema.org/deathDate> ?deathDate} .
                OPTIONAL {?s <http://schema.org/deathPlace> ?deathPlace} .
                ?s <http://purl.org/dc/terms/subjects> ?subj .
                FILTER regex(STR(?s), "%s", "i")
                }
            GROUP BY ?s ?name ?location ?description ?birthPlace ?birthDate ?deathDate ?deathPlace     
        """ % subject)

        data = self.reos.queryAndConvert()
        ret = defaultdict(lambda: '?')
        for x in data['results']['bindings']:
            for k in x.keys():
                ret[k] = x[k]['value']


        return ret
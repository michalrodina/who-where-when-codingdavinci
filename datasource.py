# # DataSource trida
# Tato trida bude poskytovat kompletni rozhrani mezi mistnimi endpointy a zdrojovou databazi plzenske knihovny

from SPARQLWrapper import SPARQLWrapper, JSON
import re

# # TODO:
# - Vyzkoumat jaky modul pouzit pro SPARQL
# - Implementovat konektor
# - Navrhnout metody pro ziskavani dat
# - Implementovat metody

class DataSource:

    ##
    # Konstruktor
    #
    # Vytvori (singleton?) spojeni s databazi plzenske knihovny
    def __init__(self):
        # REOS SPAQRL Endpoint
        self.reos = SPARQLWrapper('https://fuseki.lib-lab.cz/reos/')
        self.reos.setReturnFormat(JSON)

        # Wikidata SPARQL Endpoint
        self.wiki = SPARQLWrapper('https://query.wikidata.org/sparql')
        self.wiki.setReturnFormat(JSON)

        # Natahnout geolokacni data pro obce CR z Wikidat
        geoloc = self.get_geoloc(False)
        self.geoloc = {}
        for g in geoloc['results']['bindings']:
            self.geoloc[g['locationLabel']['value']] = g['geoloc']['value']

        pass

    def get_geoloc(self, city_label):
        self.wiki.setQuery("""
            SELECT DISTINCT ?locationLabel ?geoloc WHERE {
                ?location wdt:P17 wd:Q213.
                ?location wdt:P31 ?settlement .
                ?settlement wdt:P279 wd:Q5153359 .
                ?location rdfs:label ?cs_label .
                ?location wdt:P625 ?geoloc .
                FILTER (lang(?cs_label) = "cs") .
                #FILTER (regex((?cs_label), "%s")).

                SERVICE wikibase:label { bd:serviceParam wikibase:language "cs". }
                }

        """ % city_label)

        ret = self.wiki.queryAndConvert()

        return ret

    # Gettery:
    ##
    # Load data metoda
    #
    # Dummy getter
    def load_data(self, data_filter):
        # zpracuj data_filter

        # nacti data
        self.reos.setQuery("""
        SELECT 
            ?s 
            ?name 
            ?birthDate
            ?birthPlace 
            ?deathDate
            ?deathPlace 
            ?subj
        WHERE
          {
            ?s <http://schema.org/name> ?name .
            ?s <http://schema.org/birthDate> ?birthDate .
            ?s <http://schema.org/birthPlace> ?birthPlace .
            ?s <http://schema.org/deathDate> ?deathDate
            OPTIONAL {?s <http://schema.org/deathPlace> ?deathPlace} .
            ?s <http://purl.org/dc/terms/subjects> ?subj .
            FILTER regex(?subj, "keram", "i")
          }
        """)

        data = self.reos.queryAndConvert()
        print(data)
        ret = []
        for person in data['results']['bindings']:
            item = {}
            try:
                item['name'] = person['name']['value']
            except KeyError:
                item['name'] = 'Chyba'

            try:
                item['birthDate'] = person['birthDate']['value']

            except KeyError:
                item['birthDate'] = '?'

            try:
                item['birthPlace'] = person['birthPlace']['value']
                city = person['birthPlace']['value'].split('--')
                if city[0] in self.geoloc:
                    # print(city[0], city[1], self.geoloc[city[0]])
                    point = re.findall("\d+\.\d+",  self.geoloc[city[0]])
                    print(point)
                    item['marker'] = point
                else:
                    # print(city[0], city[1], 'Nenalezeno')
                    item['marker'] = False
            except KeyError:
                item['birthPlace'] = '?'
                item['marker'] = False

            try:
                item['deathDate'] = person['deathDate']['value']
            except KeyError:
                item['deathDate'] = '?'

            try:
                item['deathPlace'] = person['deathPlace']['value']
            except KeyError:
                item['deathPlace'] = '?'

            ret.append(item)

        return ret
        # vrat data
        return [1, 2, 3, 4]
        pass

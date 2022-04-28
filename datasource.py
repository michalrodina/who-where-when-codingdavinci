# # DataSource trida
# Tato trida bude poskytovat kompletni rozhrani mezi mistnimi endpointy a zdrojovou databazi plzenske knihovny


from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.error import HTTPError
import json
from collections import defaultdict
import re
from dataModel.village import village

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

        self.geoloc = {}
        self.okresy = self.load_geoloc()

        self.subjects = False


    def load_geoloc(self, city_label=""):

        self.wiki.setQuery("""
            SELECT DISTINCT ?locationLabel ?regionLabel ?geoloc WHERE {
                ?location wdt:P17 wd:Q213.
                ?location wdt:P131 ?region .
                ?location wdt:P31 wd:Q5153359 .
                ?location wdt:P625 ?geoloc .

                SERVICE wikibase:label { bd:serviceParam wikibase:language "cs". }
                }

        """)

        try:
            data = self.wiki.queryAndConvert()
            ret = defaultdict(list)
            for g in data['results']['bindings']:
                k = g['locationLabel']['value'] + '--' + g['regionLabel']['value'].replace('okres ', '')
                self.geoloc[k] = g['geoloc']['value']
                vil = village(k)
                ret[vil.shire].append(vil)
        except:
            print('Nepodařilo se načíst wikidata zdroj geolokace. Načítám lokální JSON zdroj.')
            fjson = open('assets/wikidata_geoloc.json', encoding='utf8')
            data = json.load(fjson) # nacist z JSONu
            for g in data:
                self.geoloc[g['locationLabel'] + '--' + g['regionLabel'].replace('okres ', '')] = \
                    g['geoloc']

        # Natahnout geolokacni data pro obce CR z Wikidat

        return ret


    def load_okresy(self, data_filter={}):
        self.reos.setQuery("""
                    SELECT DISTINCT
                        (STRAFTER(?location, '--') AS ?id)
                        (STRAFTER(?location, '--') AS ?name)
                    WHERE {
                        ?s <http://schema.org/workLocation> ?location .
                        
                    }
                    ORDER BY ASC(STRAFTER(?location, '--'))

                """)

        data = self.reos.queryAndConvert()

        ret = []
        for x in data['results']['bindings']:
            val = x['id']['value']
            if val in self.okresy:
                ret.append({"id": x['id']['value'], "name": x['name']['value']})

        return ret
        pass


    def load_obce(self, data_filter={}):
        query = """
                    SELECT DISTINCT
                        (STRBEFORE(?location, '--') AS ?id)
                        (STRBEFORE(?location, '--') AS ?name)
                    WHERE {{
                        ?s <http://schema.org/workLocation> ?location .
                        {okresFilter}
                    }}
                    ORDER BY ASC(STRBEFORE(?location, '--'))

                """


        okres = ""
        if "okres" in data_filter:
            okres = "FILTER regex(?location , \"--@location\", \"i\")".replace("@location", data_filter["okres"])

        queryToUse = query.format(okresFilter=okres)

        self.reos.setQuery(queryToUse)
        data = self.reos.queryAndConvert()

        ret = []
        for x in data['results']['bindings']:
            ret.append({"id": x['id']['value'], "name": x['name']['value']})

        return ret
        pass


    # Gettery:
    ##
    # Nacist obory pusobnosi
    #
    # TODO: Je v tom slusnej bordel :/
    def load_subjects(self):
        import csv
        if not self.subjects:
            print('Subjects not initialized')
            with open('assets/subjects.csv', mode='r', encoding='utf-8') as infile:
                reader = csv.reader(infile, delimiter=';')
                self.subjects = [{"id": rows[0], "name": rows[1]} for rows in reader]

        return self.subjects

    ##
    # Load items metoda
    #
    # Nacita vsechny polozky z datasource s vybranou mnozinou vlastnosti
    def load_items(self, data_filter):

        # nacti data
        query = """
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                               
            SELECT
                ?s 
                ?name
                ?location
                ?description
                ?birthDate
                ?birthPlace 
                ?deathDate
                ?deathPlace
                (GROUP_CONCAT(?subj;SEPARATOR="\\n") AS ?subjects)
            WHERE
            {{
                ?s <http://schema.org/name> ?name .
                ?s <http://schema.org/workLocation> ?location .
                ?s <http://schema.org/description> ?description .
                ?s <http://schema.org/birthDate> ?birthDate .
                ?s <http://schema.org/birthPlace> ?birthPlace .
                OPTIONAL {{?s <http://schema.org/deathDate> ?deathDate}} .
                OPTIONAL {{?s <http://schema.org/deathPlace> ?deathPlace}} .
                ?s <http://purl.org/dc/terms/subjects> ?subj .
                #FILTER regex(?subj, "keram", "i")
                #FILTER regex(?name, "Jan","i")
                {birthDate}
                {okresFilter}
                {obecFilter}
                {oborFilter}
                {fulltextFilter}
            }}
            GROUP BY ?s ?name ?location ?description ?birthPlace ?birthDate ?deathDate ?deathPlace
            ORDER BY ASC(?name)
        """

        # zpracuj data_filter
        # okres: Plzeň

        bday = ""
        if "birthDay" in data_filter and data_filter['birthDay'] != "":
            bday = "FILTER (?birthDate > \"@bday\"^^xsd:date)".replace("@bday", data_filter["birthDay"])

        okres = ""
        if "okres" in data_filter and data_filter['okres'] != "":
            okres = "FILTER regex(?location , \"--@location\", \"i\")".replace("@location", data_filter["okres"])

        obec = ""
        if "obec" in data_filter and data_filter['obec'] != "":
            obec = "FILTER regex(?location , \"@location--\", \"i\")".replace("@location", data_filter["obec"])

        obor = ""
        if "obor" in data_filter and data_filter['obor'] != "":
            obor = "FILTER regex(?subj , \"@subject\", \"i\")".replace("@subject", data_filter["obor"])

        fulltext = ""
        if "fulltext" in data_filter and data_filter['fulltext'] != "":
            obor = "FILTER regex(?name , \"@subject\", \"i\")".replace("@subject", data_filter["fulltext"])

        queryToUse = query.format(birthDate=bday, okresFilter=okres, obecFilter=obec, oborFilter=obor, fulltextFilter=fulltext)

        # print(queryToUse)

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

    def prepareName(self, name):
        split = name.split(', ')
        return split[1]+' '+split[0]

    ##
    # Nacist jednu osobu dle <https://svkpk.cz/resources/reos/{subject}>
    #
    # Data budou zobrazena v detailnim nahledu konkretni osoby
    #
    # @TODO: Nacist vsechny vlastnosti
    # @TODO: Zkusit dohledat fotku z wikidata/wikimedia?
    def load_item(self, subject):

        self.reos.setQuery("""
            PREFIX schema: <http://www.w3.org/2001/XMLSchema#>
            PREFIX mads:  <http://www.loc.gov/mads/rdf/v1#>
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
                #(GROUP_CONCAT(?src; SEPARATOR=";") AS ?sources)
                (?src AS ?sources)
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
                OPTIONAL {?s mads:Source ?src} .
                FILTER regex(STR(?s), "%s", "i")
                }
            GROUP BY ?s ?name ?location ?description ?birthPlace ?birthDate ?deathDate ?deathPlace ?src
            ORDER BY ASC(?name)    
        """ % subject)

        data = self.reos.queryAndConvert()
        print(data)
        ret = defaultdict(lambda: '?')
        for x in data['results']['bindings']:
            for k in x.keys():
                ret[k] = x[k]['value']

        query = """
                             PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT distinct ?item ?itemLabel ?image WHERE 
        {{
          ?item wdt:P31 wd:Q5.
          ?item ?label \"{name}\"@cs .
          ?item wdt:P569 ?P569_2.
          ?item wdt:P18 ?image
          BIND("{born}"^^xsd:dateTime AS ?P569_2)
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "cs". }}
        }}
                        """
        usedQuery = query.format( name = self.prepareName(ret["name"]), born = ret["birthDate"])

        self.wiki.setQuery(usedQuery)
        try:
            dataImage = self.wiki.queryAndConvert()
            # print(dataImage)
            ret["image"] = dataImage['results']['bindings'][0]['image']['value']
        except HTTPError:
            ret['image'] = False
            # print('WikiData HTTP Error')
        except (IndexError, KeyError) as e:
            ret['image'] = False
            # print(e)
            # print('WikiData Data Error')
        #try:
        #    ret["image"] = dataImage['results']['bindings'][0]['image']['value']


        return ret
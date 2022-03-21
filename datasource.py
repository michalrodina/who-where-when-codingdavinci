# # DataSource trida
# Tato trida bude poskytovat kompletni rozhrani mezi mistnimi endpointy a zdrojovou databazi plzenske knihovny

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
        # pripoj sparql datasource
        pass

    # Gettery:
    ##
    # Load data metoda
    #
    # Dummy getter
    def load_data(self, data_filter):
        # zpracuj data_filter

        # nacti data

        # vrat data
        return [1, 2, 3, 4]
        pass

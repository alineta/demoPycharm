import dash
import dash_cytoscape as cyto
import dash_html_components as html
from lireOracle import lireOracle

def initListeElements():
    lt = lireOracle()
    lt.lecture()
    listeElements = []
    for i in lt.listeTables.nom_table :
        listeElements.append({'data': {'id': i, 'label': i}})

    for index, i in lt.listeRelTab.iterrows() :
        listeElements.append({'data': {'source': i['table_parent'], 'target': i['table_enfant']}})
    return listeElements

def executeDash(listeElements):
    app = dash.Dash(__name__)

    app.layout = html.Div([
        cyto.Cytoscape(
            id='lesTables',
            layout={'name': 'circle', 'radius': 20},
            elements=listeElements
        )
    ])
    app.run_server(debug=False)


if __name__ == '__main__':
    listeElements = initListeElements()
    executeDash(listeElements)
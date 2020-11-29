import pandas as pd
import networkx as nx
import dash
import dash_table
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from CréerDFTablesOracle import DfRelationsTables
from CréerDFTablesOracle import DfListeTables
from CréerDFTablesOracle import CytoHTML
from CréerDFTablesOracle import CytoNoeudHTML
from CréerDFTablesOracle import ListeDeroulanteTables
from CréerDFTablesOracle import ListeTables
from CréerDFTablesOracle import getAttributTable
from CréerDFTablesOracle import initAffichage
from utilitaires import getRoot
#___ Récupération des DF des queries SQL

dfListeRelation = DfRelationsTables()
dfListeTables = DfListeTables()

#_******__Codage pour les noeuds et les relations
#___ ________Préparation des listes pour les noeuds
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#******  initialisation variables
listeNoeudsRelHTML = []
listeDeroulanteTables = []
ListeNoeuds =[]
listeCytoHTMLPart=[]
listeNoeudsRelNew = []
NoeudSelec=[]
valeur=''

Dfliste =[]

#_______ Param Affichage HTML Cytoscape et Dropdown
CytoNoeudHTML(dfListeTables,listeNoeudsRelHTML)
listeCytoHTML=CytoHTML(dfListeRelation,listeNoeudsRelHTML)


#_______ Param Affichage Liste déroulante pour la sélection
#           des tables par l'utilisateur

listeDeroulanteNoeuds=ListeDeroulanteTables(dfListeTables)

#_______


#__________________Gestion du Front______________________

card_main = dbc.Card(
    [
        dbc.CardImg(src="/assets/img_etl.jpg", top=True, bottom=False,
                    title="Image by Elena", alt='ETL Architecture'),
        dbc.CardBody(
            [
                html.P("Choix des dispositions", style={'text-align': 'center'}, className="card-title"),
                dcc.Dropdown(
                    id='dropdown-update-layout',
                    value='breadthfirst',
                    clearable=False,
                    options=[
                        {'label': name.capitalize(), 'value': name}
                        for name in ['grid', 'breadthfirst', 'circle', 'cose', 'concentric','random']
                    ]
                ),
            ]
        ),
        dbc.CardBody([
            html.P("Créer la reqête", style={'text-align': 'center'}, className="card-title"),
            dbc.Button("Création", color="primary", style={'button-align': 'center'}),
            html.P(''),
            html.P("Générer la reqête", style={'text-align': 'center'}, className="card-title"),
            dbc.Button("Génération", color="primary", style={'button-align': 'center'})
        ])
    ],
    color="primary",   # https://bootswatch.com/default/ for more card colors
    inverse=False,   # change color of text (black or white)
    outline=True,  # True = remove the block colors from the background and header
)

df = getAttributTable('COMMANDES')

card_question = dbc.Card(
    [
        html.H3("La requête SQL", style={'text-align': 'center'}, className="card-title"),
        html.Div(id='textarea-requete', style={'whiteSpace': 'pre-line','text-align': 'left'}),
    ],
    color="primary",
    inverse=False,
    outline=True,
)

card_graph = dbc.Card(
    [
        html.H3("Projet ETL", style={'text-align': 'center'}, className="card-title"),
        html.H4("Visualisation des relations entre les tables de la base de données Oracle et génération de requêtes",
                style={'text-align': 'center'}, className="card-text"),
        cyto.Cytoscape(
            id='cytoscape-update-layout',
            elements=[],
            layout={'name': 'breadthfirst'},
            style={'width': '100%', 'height': '400px'}
            ),
        cyto.Cytoscape(
            id='cytoscape-global',
            elements=listeCytoHTML,
            layout={'name': 'breadthfirst'},
            style={'width': '100%', 'height': '400px'}
        ),
        html.Div(id='affiche-colonnes-table'),
    ]
)

app.layout = html.Div([
    dbc.Row([dbc.Col(card_main, width=2),
             dbc.Col(card_question, width=3),
             dbc.Col(card_graph, width=7)], justify="around"),  # justify="start", "center", "end", "between", "around"
])

#_____________ Gestion des Output, Input _______

@app.callback([Output(component_id='cytoscape-update-layout',component_property= 'layout'),
               Output(component_id='cytoscape-global',component_property= 'layout'),],
               Input(component_id='dropdown-update-layout',component_property= 'value'),
              State(component_id='cytoscape-update-layout', component_property='layout'),
              prevent_initial_call=True
              )
def updateDropdownLayout(nouveauLayout,ancienLayout):
    if nouveauLayout :
        return {'name': nouveauLayout},{'name': nouveauLayout}
    else :
        return ancienLayout,ancienLayout

table_selectionnee = ''
@app.callback(Output('affiche-colonnes-table', 'children'),
              [Input(component_id="cytoscape-update-layout",component_property= 'tapNodeData')],
              prevent_initial_call=True
              )
def updateTable(table):
    global table_selectionnee
    if table :
        table_selectionnee = table['id']

    df = getAttributTable(table_selectionnee)
    tableAffichage = html.Div([
        html.H5(table_selectionnee),
        dash_table.DataTable(
            data=df.to_dict('rows'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        )
    ])

    return  tableAffichage

reqSQL = ''
@app.callback(Output('textarea-requete', 'children'),
              [Input(component_id="cytoscape-update-layout",component_property= 'selectedEdgeData')],
              prevent_initial_call=True
              )
def update_requette(relation):
    return reqSQL


@app.callback([Output(component_id='cytoscape-update-layout',component_property= 'elements')],
              [Input(component_id="cytoscape-global",component_property= 'tapNodeData'),
               Input(component_id="cytoscape-update-layout",component_property= 'tapNodeData'),
               Input(component_id="cytoscape-update-layout",component_property= 'selectedEdgeData')],
               [State(component_id='cytoscape-update-layout',component_property= 'elements')],
               prevent_initial_call=True
)
def update_layout1(table1, table2, relations, graph):
    global reqSQL
    reqSQL = ''

    if table2 is None:
        table = table1
        if table:
            if (len(table) > 0) & (len(graph) == 0):
                noeud = table['id']
                print(len(table), len(graph),noeud)
                return [initAffichage(dfListeRelation, noeud)]
    else :
        table = table2
        noeud = table['id']
        return [initAffichage(dfListeRelation, noeud)]

    if relations is None:
        return [graph]
    else:
        if len(relations) > 0:
            valeurtab = []
            premiereTable = getRoot(graph)#relations[0]['source']
            reqSQL = '-'*70+'\nselect count(*) \nfrom '+ premiereTable
            for ligne in relations:
                if ligne['source'] not in valeurtab:
                    valeurtab.append(ligne['source'])

                    if premiereTable == ligne['source']:
                        table_suivante1,table_suivante2 = ligne['target'],ligne['source']

                    else:
                        table_suivante1,table_suivante2 = ligne['source'],ligne['target']

                    reqSQL += "\n     join {0} \n       on {0}.{2} = {1}.{3} ".format(
                        table_suivante1,table_suivante2,
                    ligne['relation']['colTableMère'],
                        ligne['relation']['colTableFille'])
            reqSQL += '\n'
            with open('liste_requetes.txt', mode='a', encoding='utf-8') as mon_fichier :
                mon_fichier.write(reqSQL)

    return [graph]

    # if table is None:
    #     return [graph]
    # else:
    #     if len(table) > 0:
    #         noeud = table['id']
    #         return [initAffichage(dfListeRelation, noeud)]
    #     else:
    #         if relations:
    #             if len(relations) > 0:
    #                 valeurtab = []
    #                 premiereTable = getRoot(graph)#relations[0]['source']
    #                 reqSQL = '-'*70+'\nselect count(*) \nfrom '+ premiereTable
    #                 for ligne in relations:
    #                     if ligne['source'] not in valeurtab:
    #                         valeurtab.append(ligne['source'])
    #
    #                         if premiereTable == ligne['source']:
    #                             table_suivante1,table_suivante2 = ligne['target'],ligne['source']
    #
    #                         else:
    #                             table_suivante1,table_suivante2 = ligne['source'],ligne['target']
    #
    #                         reqSQL += "\n     join {0} \n       on {0}.{2} = {1}.{3} ".format(
    #                             table_suivante1,table_suivante2,
    #                         ligne['relation']['colTableMère'],
    #                             ligne['relation']['colTableFille'])
    #                 reqSQL += '\n'
    #                 with open('liste_requetes.txt', mode='a', encoding='utf-8') as mon_fichier :
    #                     mon_fichier.write(reqSQL)
    #
    #         return [graph]

if __name__ == '__main__':
    app.run_server(debug=True)
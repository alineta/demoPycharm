import pandas as pd
import dash
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
from CréerDFTablesOracle import DfListeAttributTable
from CréerDFTablesOracle import initAffichage

#___ Récupération des DF des queries SQL

dfListeRelation = DfRelationsTables()
#print(type(DfListeRel))
dfListeTables = DfListeTables()
#print(type(DfListeTables))

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
print(listeCytoHTML)



#_______ Param Affichage Liste déroulante pour la sélection
#           des tables par l'utilisateur

listeDeroulanteNoeuds=ListeDeroulanteTables(dfListeTables)
#print (listeDeroulanteNoeuds)

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
                    value='circle',
                    clearable=False,
                    options=[
                        {'label': name.capitalize(), 'value': name}
                        for name in ['grid', 'random', 'circle', 'cose', 'concentric']
                    ]
                ),
                # html.P(''),
                # html.P("Choix des tables", style={'text-align': 'center'}, className="card-title"),
                # dcc.Dropdown(
                #     id='ChoixTables',
                #     options=listeDeroulanteNoeuds,
                #     multi=False
                # )

                # dbc.Button("Press me", color="primary"),
                # dbc.CardLink("GirlsWhoCode", href="https://girlswhocode.com/", target="_blank"),
            ]
        ),
    ],
    color="primary",   # https://bootswatch.com/default/ for more card colors
    inverse=False,   # change color of text (black or white)
    outline=True,  # True = remove the block colors from the background and header
)


card_question = dbc.Card(
    [
        dbc.CardBody([
            html.P("Créer la reqête", style={'text-align': 'center'}, className="card-title"),
            dbc.Button("Création", color="primary", style={'button-align': 'center'}),
            html.P(''),
            html.P("Générer la reqête", style={'text-align': 'center'}, className="card-title"),
            dbc.Button("Génération", color="primary", style={'button-align': 'center'})
        ]),
    ],
    color="warning",
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
            elements=listeCytoHTML,
            layout={'name': 'circle'},
            style={'width': '100%', 'height': '400px'}
            )
    ]
)


app.layout = html.Div([
    dbc.Row([dbc.Col(card_main, width=2),
             dbc.Col(card_question, width=2),
             dbc.Col(card_graph, width=7)], justify="around"),  # justify="start", "center", "end", "between", "around"

    # dbc.CardGroup([card_main, card_question, card_graph])   # attaches cards with equal width and height columns
    # dbc.CardDeck([card_main, card_question, card_graph])    # same as CardGroup but with gutter in between cards

    # dbc.CardColumns([                        # Cards organised into Masonry-like columns
    #         card_main,
    #         card_question,
    #         card_graph,
    #         card_question,
    #         card_question,
    # ])

])



# app.layout =html.Div([
#         dcc.Dropdown(
#                 id='dropdown-update-layout',
#                 value='circle',
#                 clearable=False,
#                 options=[
#                     {'label': name.capitalize(), 'value': name}
#                     for name in ['grid', 'random', 'circle', 'cose', 'concentric']
#                 ]
#             ),
#         cyto.Cytoscape(
#                 id='cytoscape-update-layout',
#                 elements=listeCytoHTML,
#                 layout={'name': 'circle'},
#                 style={'width': '100%', 'height': '450px'}
#             ),
#
#         dcc.Dropdown(
#                 id='ChoixTables',
#                 options=listeDeroulanteNoeuds,
#     #            value='NYC',
#                 placeholder= 'table(s) sélectionnée(s)',
#                 multi=False
#         ),
#         html.Div(id='dd-output-container')
#     ])

#_____________ Gestion des Output, Input _______

@app.callback(Output(component_id='cytoscape-update-layout',component_property= 'layout'),
               Input(component_id='dropdown-update-layout',component_property= 'value'),
              State(component_id='cytoscape-update-layout', component_property='layout')
              )
def updateDropdownLayout(nouveauLayout,ancienLayout):
    if nouveauLayout :
        return {'name': nouveauLayout}
    else :
        return ancienLayout


# @app.callback( Output(component_id='cytoscape-update-layout',component_property= 'elements'),
#                Input(component_id='ChoixTables',component_property= 'value'),
#                State(component_id='cytoscape-update-layout',component_property= 'elements'))
# def updateDropdownChoixTables(table,elements):
#     print(table)
#     if table :
#         return [initAffichage(dfListeRelation, table)]
#     # else:
#     #     return [elements]

@app.callback([#Output(component_id='cytoscape-update-layout',component_property= 'style'),
              Output(component_id='cytoscape-update-layout',component_property= 'elements')],
              [Input(component_id="cytoscape-update-layout",component_property= 'selectedNodeData')],
               #Input(component_id="cytoscape-update-layout",component_property= 'selectedEdgeData')],
               State(component_id='cytoscape-update-layout',component_property= 'elements')
)
def update_layout1(table, graph):
    print(table, graph)
    if table is None :
        print('aucune sélection',graph)
        return [graph]
    else:
        if len(table)>0:
            noeud=table[0]['id']
            print("select count from "+table[0]['id'])
            return [initAffichage(dfListeRelation,noeud)]
        else:
            return [graph]

if __name__ == '__main__':
    app.run_server(debug=True)
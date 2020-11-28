# fichier acces a la bdd + extraction elements
# df_to et df sont les df completes
# df > nodeA, nodeB, conn_node, conn_nodeB
# df_to =  node, column, conn_node
import pandas as pd
import sqlalchemy
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
import os

def lireBaseDeDonnees(connexion):
    """

    :param connexion:
    :return:
    """
    if len(connexion) < 1:
        connexion = "oracle+cx_oracle://stag08:Phoenix#Icar67@51.91.76.248:15440/coursdb"
    engine = sqlalchemy.create_engine(connexion, max_identifier_length=128)
    connection = engine.connect()
    query = """
                select ut.table_name as node
                from user_tables ut
    """
    tables = pd.read_sql_query(query, connection)

    query = """
                select tbe.CONSTRAINT_NAME        as "nom_contrainte",  
                           tbm.TABLE_NAME         as "table_parent",
                           clm.COLUMN_NAME        as "col_tab_parent",
                           tbe.TABLE_NAME         as "table_enfant",
                           cle.COLUMN_NAME        as "col_tab_enfant" 
                from user_constraints tbe 
                     join user_cons_columns cle
                       on  tbe.TABLE_NAME      = cle.TABLE_NAME
                       and tbe.CONSTRAINT_NAME = cle.CONSTRAINT_NAME 
                     join user_constraints tbm 
                       on tbm.CONSTRAINT_NAME = tbe.R_CONSTRAINT_NAME 
                     join user_cons_columns clm
                       on  tbm.TABLE_NAME      = clm.TABLE_NAME
                       and tbm.CONSTRAINT_NAME = clm.CONSTRAINT_NAME 
                where tbe.CONSTRAINT_TYPE = 'R'
        """
    tableReferences = pd.read_sql_query(query, connection)

    query = """
            select  
                   tc.TABLE_NAME                                                 as "nom_table",
                   tc.COLUMN_ID                                                  as "id_colonne",
                   tc.COLUMN_NAME                                                as "nom_colonne",
                   lower(tc.DATA_TYPE)                                           as "type_colonne",
                   nvl(to_char(coalesce(tc.DATA_PRECISION, tc.DATA_LENGTH)),' ') as "taille_colonne",
                   nvl(to_char(tc.DATA_SCALE),' ')                               as "precision_colonne",
                   decode(tc.NULLABLE,'Y','null','N','not null')                 as "is_nullable",
                   nvl(ky.CONSTRAINT_TYPE,' ')                                   as "type_contrainte", 
                   nvl(ky.CONSTRAINT_NAME,' ')                                   as "nom_contrainte"
            from user_tab_columns tc
                 left join (select                             
                               co.OWNER                   ,
                               co.TABLE_NAME              ,
                               cc.COLUMN_NAME             ,
                               co.CONSTRAINT_TYPE||'K'  as CONSTRAINT_TYPE,
                               co.CONSTRAINT_NAME         
                        from user_constraints co 
                             join user_cons_columns cc
                               on  co.TABLE_NAME      = cc.TABLE_NAME
                               and co.CONSTRAINT_NAME = cc.CONSTRAINT_NAME 
                        where co.CONSTRAINT_TYPE in ('P','U')) ky
                  on (     tc.TABLE_NAME     = ky.TABLE_NAME  
                       and tc.COLUMN_NAME    = ky.COLUMN_NAME  )

    """
    tableColonnes = pd.read_sql_query(query, connection)
    return tables, tableReferences, tableColonnes


# init Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], title='EasyRequest')

listeElements = []
# LAYOUT

# ATTRIBUT HTML STYLE (classes non assignées dans css, propres à dash)
# pour pouvoir scroller etc

styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {'height': 'calc(98vh - 115px)'}
}

# ATTRIBUTION DU TEXT AREA HTML
# DIV CYTOSCAPE


app.layout = dbc.Container([
    html.Div(id='layout1', children=[
        html.Div(className='eight columns', children=[
            html.Br(),
            html.H1(
                children='EasyRequest',
                style={
                    'textAlign': 'center',
                    'color': '#d55a79',
                    'font-family': 'montserrat'
                }),
            html.Br(),
            cyto.Cytoscape(
                id='cytoscape',
                elements=listeElements,
                boxSelectionEnabled=True,
                layout={'name': 'breadthfirst'},
                style={
                    'height': '400px',
                    'width': '100%',
                    'background-color': '#bdc3c7',
                    'border': '2px #d55a79 solid',
                    'padding': '5px',
                    'border-radius': '0px 0px 10px 10px ',
                    'box-shadow': ' 0 0 20px 0 rgba(0, 0, 0, 0.2), 0 5px 5px 0 rgba(0, 0, 0, 0.24)'
                },
                stylesheet=[
                    # Nodes
                    {
                        'selector': 'node',
                        'style': {
                            'background-color': '#d55a79',
                            'content': 'data(label)',
                            'color': '#b73c5b',
                            'font-family': 'montserrat, sans-serif'
                        }
                    },
                    # Edges
                    {
                        'selector': 'edge',
                        'style': {
                            'line-color': '#7f8c8d'
                        }
                    },
                    # Selected nodes and edges
                    {
                        'selector': ':selected',
                        'style': {
                            'background-color': 'white',
                            'line-color': 'white'
                        }
                    },
                ]
            ),
            html.Br(),
            html.Br(),
            html.Div(id='sql', children=[
                html.Div(id='hsql', children=[("Affichage requête SQL")], style={'border': '2px #d55a79 solid',
                                                                                 'background-color': '#d55a79',
                                                                                 'border-radius': '1px',
                                                                                 'text-align': 'center'}),
                dcc.Textarea(
                    id='sortie_requete_SQL',
                    value='',
                    style={'width': '100%', 'height': '100px',
                           'background': '#bdc3c7',
                           'box-sizing': 'border-box',
                           'border': '0',
                           'border-radius': '0px 0px 10px 10px ',
                           'font-size': '13px',
                           'max-height': '200px',
                           'padding': '5px'}
                )])
        ]),
        html.Br(),
        html.Br(),
        html.Div(id='form', children=[
            html.Div(id='hconnex', children=[("Connectez vous à une base")], style={'border': '2px #d55a79 solid',
                                                                                    'background-color': '#d55a79',
                                                                                    'border-radius': '1px',
                                                                                    'text-align': 'center'}),
            dcc.Input(id="lib", type="text", placeholder="Entrer la librairie de connexion",
                      value="oracle+cx_oracle", style={'width': '17%', 'border-radius': '0px 0px 0px 10px '}),
            dcc.Input(id="user", type="text", placeholder="Entrez l'id user", value="stag08", style={'width': '15%'}),
            dcc.Input(id="Password", type="password", placeholder="Entrez le mot de passe",
                      value="Phoenix#Icar67", style={'width': '17%'}),
            dcc.Input(id="ip", type="text", placeholder="Entrer l'adresse ip de la bdd",
                      value="51.91.76.248", style={'width': '17%'}),
            dcc.Input(id="Port", type="text", placeholder="Entrez le port", value="15440", style={'width': '17%'}),
            dcc.Input(id="dossier", type="text", placeholder="Entrer votre nom de dossier",
                      value="coursdb", style={'width': '17%', 'border-radius': '0px 0px 10px 0px '}),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col(),
                dbc.Col(dbc.Button('valider',
                                   block=True,
                                   id='submit-button',
                                   className='mb-3',
                                   n_clicks=0,
                                   style={'background': '#d55a79',
                                          'border-radius': '10px',
                                          'box-shadow': '6px 6px 20px 4px (0, 0, 0, 0.5)',
                                          'text-transform': 'uppercase'
                                          }
                                   )),
                dbc.Col()
            ]),
        ]),
        html.Br(),
        html.Br()
    ])])


# def pour réaliser la vérification des edges et nodes
def verification(selected_node, selected_edge):
    list_tables = set()  # pour mettre les composants de l'élément dans une liste
    list_edges = set()

    for e in selected_node:
        list_tables.add(e['id'])  # créer une liste qui retourne les composants de la source du node
    for e in selected_edge:
        list_edges.add(e['source'])  # créer une liste qui retourne les composants de la source du node
        list_edges.add(e['target'])  # créer une liste qui retourne les composants de la source du node
    if sorted(list_tables) == sorted(list_edges):
        return True
    else:
        return False


@app.callback(Output('sortie_requete_SQL', 'value'),
              [Input('cytoscape', 'selectedEdgeData'),
               Input('cytoscape', 'selectedNodeData')])
def testing(selected_edge, selected_node):
    if (selected_node is None or len(selected_node) == 0) and (selected_edge is None or len(selected_edge) == 0):
        return None
    elif len(selected_node) == 1 and (selected_edge is None or len(selected_edge) == 0):
        return 'SELECT * FROM ' + selected_node[0]['id']
    elif verification(selected_node, selected_edge) == False:
        return "La requête n'est pas complète, merci de sélectionner des noeuds valides et les contraintes associées."
    else:
        req = 'SELECT * FROM ' + selected_node[0]['id']
        test = [selected_node[0]['id']]
        for x in selected_edge:
            if x['source'] not in test:
                test.append(x['source'])
                req += ' \n JOIN ' + x['source'] + ' ON ' + x['target'] + '.' + x['coltarget'] + \
                       ' = ' + x['source'] + '.' + x['colsource']
            else:
                test.append(x['target'])
                req += ' \n JOIN ' + x['target'] + ' ON ' + x['source'] + '.' + x['colsource'] + \
                       ' = ' + x['target'] + '.' + x['coltarget']
        print(req)

        repertoire = "C:/SimplonIA/projet_ETL/"
        if not os.path.exists(repertoire):
            os.makedirs(repertoire)

        with open(repertoire+"test.txt", "a") as myfile:
            myfile.write('\n' + req + '\n')
        return req


@app.callback(
    [Output('cytoscape', 'elements')],
    Input('submit-button', 'n_clicks'),
    [State('lib', 'value'),
     State('user', 'value'),
     State('Password', 'value'),
     State('ip', 'value'),
     State('Port', 'value'),
     State('dossier', 'value')])
def update_output(n_clicks, lib, user, password, ip, port, dossier):
    global listeElements
    print(n_clicks, lib, user, password, ip, port, dossier)
    if n_clicks < 1: return [listeElements]

    connex = "{}://{}:{}@{}:{}/{}".format(lib, user, password, ip, port, dossier)
    print(connex)
    tables, tableReferences, tableColonnes = lireBaseDeDonnees(connex)
    listeElements = []
    for i in tables.node:
        listeElements.append({'type': 'node', 'data': {'id': i, 'label': i}})

    for index, i in tableReferences.iterrows():
        listeElements.append({'type': 'edge', 'data': {'source': i['table_parent'], 'target': i['table_enfant'],
                                                       'colsource': i['col_tab_parent'],
                                                       'coltarget': i['col_tab_enfant'], 'edge': i['nom_contrainte']}})

    return [listeElements]


if __name__ == '__main__':
    app.run_server(debug=True)

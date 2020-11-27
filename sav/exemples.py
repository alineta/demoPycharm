import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from lireOracle import lireOracle


def initListeElements():
    lt = lireOracle()
    lt.lecture()

    listeElements = []
    for i in lt.listeTables.nom_table :
        listeElements.append({'data': {'id': i, 'label': i}})

    for index, i in lt.listeRelTab.iterrows() :
        listeElements.append({'data': {'source': i['table_parent'], 'target': i['table_enfant']}})

    listeTables = [ i for i in lt.listeTables.nom_table]
    return listeTables,listeElements



class myDash():

    def __init__ ( self):
        self.myapp = dash.Dash(__name__)
        self.listeTables, self.listeElements = initListeElements()

        self . default_stylesheet = [
                {
                    'selector': 'node',
                    'style': {
                        'background-color': '#BFD7B5',
                        'label': 'data(label)'
                    }
                },
                {
                    'selector': 'edge',
                    'style': {
                        'line-color': '#A3C4BC'
                    }
                }
            ]

    def initLayout(self):
        self.myapp.layout = html.Div([
            html.Div([
                html.Div(style={'width': '50%', 'display': 'inline'}, children=[
                    'Edge Color:',
                    dcc.Input(id='input-line-color', type='text')
                ]),
                html.Div(style={'width': '50%', 'display': 'inline'}, children=[
                    'Node Color:',
                    dcc.Input(id='input-bg-color', type='text')
                ]),
                dcc.Dropdown(
                    id="dp_tables",
                    options=[{"label": str(nom_table), "value": str(nom_table)}  for nom_table in self.listeTables],
                    multi=True,
                    value=list(self.listeTables),
                    className="dcc_control",
                ),
            ]),
            cyto.Cytoscape(
                id='lesTables',
                layout={'name': 'circle', 'radius': 20},
                stylesheet=self.default_stylesheet,
                style={'width': '100%', 'height': '450px'},
                elements=self.listeElements
            )
        ])

    def initCallbacks(self):

        @self.myapp.callback(Output('lesTables', 'stylesheet'),
                       Input('input-line-color', 'value'),
                       Input('input-bg-color', 'value'))
        def update_stylesheet(line_color, bg_color):
            if line_color is None:
                line_color = 'transparent'

            if bg_color is None:
                bg_color = 'transparent'

            new_styles = [
                {
                    'selector': 'node',
                    'style': {
                        'background-color': bg_color
                    }
                },
                {
                    'selector': 'edge',
                    'style': {
                        'line-color': line_color
                    }
                }
            ]

            return self.default_stylesheet + new_styles

        @self.myapp.callback(
            Output('lesTables', 'elemnents'),
            [
                Input("dp_tables", "value"),
                #Input('lesTables', 'elemnents'),
            ],
        )
        def update_dp_table(dp_tables):
            print(dp_tables)
            return self.listeElements


    def run_server(self, *args, **kwargs):
        self.myapp.run_server(*args, **kwargs)


if __name__ == '__main__':
    app = myDash()
    app.initLayout()
    app.initCallbacks()

    app.run_server(debug=False)
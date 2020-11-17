import dash
import dash_cytoscape as cyto
import dash_html_components as html

app = dash.Dash(__name__)


app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape-two-nodes',
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '400px'},
        elements=[
            {'data': {'id': 'commandes', 'label': 'commandes'}, 'position': {'x': 75, 'y': 75}},
            {'data': {'id': 'details_commandes', 'label': 'details_commandes'}, 'position': {'x': 200, 'y': 200}},
            {'data': {'id': 'produits', 'label': 'produits'}, 'position': {'x': 20, 'y': 20}},
            {'data': {'source': 'commandes', 'target': 'details_commandes'}},
            {'data': {'source': 'details_commandes', 'target': 'produits'}}
        ]
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
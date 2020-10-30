import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(name=__name__, external_stylesheets=external_stylesheets)

countries = {
    'America':['NY', 'SF', 'Cinn'],
    'Canada':['Montreal','Toronto','Ottawa']
}

app.layout = html.Div([
    dcc.RadioItems(
        id='country_dropdown',
        options=[ {'label':k, 'value':k} for k in countries.keys()],
        value= 'America'
    ),
    html.Hr(),

    dcc.RadioItems(id='city_dropdown'),
    html.Hr(),

    html.Div(id='display_selected_values'),
    html.Hr()
])

@app.callback(
    Output('city_dropdown', 'options'),
    [Input('country_dropdown', 'value')]
)
def set_city_options(selected_country):
    return [ {'label': i + 'label', 'value': i} for i in countries[selected_country]]

#need a callback for select city even though not select
@app.callback(
    Output('city_dropdown','value'),
    [Input('city_dropdown','options')]
)
def set_city_value(city_options):
    return city_options[0]['value']

@app.callback(
    Output('display_selected_values', 'children'),
    [Input('country_dropdown', 'value'),
     Input('city_dropdown', 'value')]
)
def set_display_selected_values(selected_country, selected_city):
    return 'You have selected: ' + selected_city + ' in ' + selected_country
if __name__=='__main__':
    app.run_server(debug=True)



import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

app = dash.Dash()

df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')
available_indicators = df['Indicator Name'].unique()
print(df)
app.layout = html.Div([
    html.H1("Country indicator"),
    html.H2("Legend"),
    html.Div([
        html.Div([
            dcc.Dropdown(id='xaxis-column',
            options= [ {'label': i, 'value': i} for i in available_indicators],
            value = 'CO2 emissions (metric tons per capita)'),
            dcc.RadioItems(
                id='xaxis-type',
                options = [{'label':i, 'value':i} for i in ['Linear', 'Log']],
                value = 'Linear',
                labelStyle = {'display': 'inline-block'}
            )
        ],
        style = {'width':'48%', 'display':'inline-block'}
        ),

        html.Div([
            dcc.Dropdown(id='yaxis-column',
            options= [ {'label': i, 'value': i} for i in available_indicators],
            value = 'Services, etc., value added (% of GDP)'),
            dcc.RadioItems(
                id='yaxis-type',
                options = [{'label':i, 'value':i} for i in ['Linear', 'Log']],
                value = 'Linear',
                labelStyle = {'display': 'inline-block'}
            )
        ],
        style = {'width':'48%', 'display':'inline-block'}
        )
    ]),

    dcc.Graph(id='graph_id'),

    dcc.Slider(
        id='slider_id',
        min=df['Year'].min(),
        max=df['Year'].max(),
        value = df['Year'].max(),
        marks= {str(year): str(year) for year in df['Year'].unique()},
        step = None
        )


])

@app.callback(
    Output(component_id = 'graph_id', component_property='figure'),
    [Input(component_id= 'xaxis-column', component_property='value'),
     Input( component_id= 'xaxis-type', component_property='value'),
     Input(component_id = 'yaxis-column', component_property='value'),
     Input( component_id='yaxis-type', component_property='value'),
     Input( component_id='slider_id', component_property='value')
    ]
)
def update_graph(xaxis_column_name, xaxis_column_type,yaxis_column_name,
                yaxis_column_type, year_value):
    dff = df[df['Year']==year_value]
    x = dff[ dff['Indicator Name'] == xaxis_column_name]['Value']
    y = dff[ dff['Indicator Name'] == yaxis_column_name]['Value']

    fig = px.scatter( x =x, y = y,
                        hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])
    fig.update_xaxes( title=xaxis_column_name, 
                        type = 'linear' if xaxis_column_type=='Linear' else 'log')
    fig.update_yaxes( title=yaxis_column_name,
                        type= 'linear' if yaxis_column_type=='Linear' else 'log')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
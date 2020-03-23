import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import chart_studio.plotly
import chart_studio.plotly as ply
import plotly.graph_objs as go
import plotly.express as px


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +
       '$select=spc_common,boroname,health,steward,count(tree_id)' +
       '&$group=spc_common,boroname,health,steward').replace(' ', '%20')


def paging(data, test):
    return pd.concat([data, test])


df = pd.read_json(url)
df_all = pd.DataFrame()
incre = 0
while True:

    if df.empty:
        break
    else:

        df_all = paging(df_all, df)
        incre += 1
        df = pd.read_json(url + '&$offset=' + str(incre) + '000')

df_all.dropna()


app.layout = html.Div([
    html.Div([
    html.H1(children='Tree NYC'),
    html.H4(children='Dropdown by Borough and Species')]),
    html.Div([
    dcc.Dropdown(
        id='borough',
        options=[
            {'label': i, 'value': i}
            for i in df_all['boroname'].dropna().unique()
        ],
        value='Manhattan',
        multi=False,
        className="dcc_control"
        
    ),
    dcc.Dropdown(
        id='species',
        options=[
            {'label': i, 'value': i}
            for i in df_all['spc_common'].dropna().unique()
        ],
        value='red maple',
        multi=False,
        className="dcc_control"
        
    )]

    ),
    html.Div([
    dcc.Graph(id='graph_1')],
    className="mini_container"),
    html.Div([
    html.H4(children='Tree Health by Steward '),
    dcc.Graph(id='graph_2')

    ],className="mini_container" )
])


@app.callback(
    dash.dependencies.Output('graph_1', 'figure'),
    [dash.dependencies.Input('borough', 'value'),
     dash.dependencies.Input('species', 'value')])
def Graph_1(borough_value, species_value):
    one_case_filter = df_all[(df_all['boroname'] == borough_value) &
                             (df_all['spc_common'] == species_value)]
    health_count = one_case_filter.groupby('health').sum()['count_tree_id']

    return {"data": [go.Bar(x=health_count.index, y=health_count)],
            "layout": go.Layout(title=" Tree Health Count")}


@app.callback(
    dash.dependencies.Output('graph_2', 'figure'),
    [dash.dependencies.Input('borough', 'value'),
     dash.dependencies.Input('species', 'value')])
def Graph_2(borough_value, species_value):
    one_case_filter = df_all[(df_all['boroname'] == borough_value) &
                             (df_all['spc_common'] == species_value)]
    health_count = one_case_filter.groupby('health').sum()['count_tree_id']
    steward_count = one_case_filter.groupby('steward').sum()['count_tree_id']

    tree_steward = pd.merge(one_case_filter,
                            pd.DataFrame(steward_count),
                            on='steward')

    tree_steward['percent'] = round(
        tree_steward['count_tree_id_x']/tree_steward['count_tree_id_y'] * 100, 2)

    df = px.data.tips()
    fig = px.bar(tree_steward, x="steward",
                 y="percent", color='health', barmode='group')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
    

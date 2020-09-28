import dash
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import Flask
import plotly.express as px
from arcgis import GIS

import numpy as np
import pandas as pd

gis = GIS();
item = gis.content.get("f7d1318260b14ac2b334e81e55ee5c9e#data");
flayer = item.layers[0];
daily_df = pd.DataFrame.spatial.from_layer(flayer);
daily_df.rename(columns = {'Cases':'Total Cases', 'ActiveCases':'Active Cases', 'HA_Name':'Health Authority', 'Recovered':'Recovered Cases'}, inplace = True)

df = pd.read_csv("http://www.bccdc.ca/Health-Info-Site/Documents/BCCDC_COVID19_Dashboard_Case_Details.csv")
df.rename(columns = {"Reported_Date":"Reported Date"}, inplace = True)
most_recent = df['Reported Date'].iloc[-1]

## daily count of covid cases
covid_count = df.groupby(by = "Reported Date").count()
previous_covid_cases = covid_count.iloc[-2][0]
BC_active_cases = daily_df['Active Cases'].sum()
one_week_trend = covid_count.Sex.tail(7).sum()

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
server = app.server
app.title = "Proof of Care - COVID Dashboard"

# Age and Sex Graph Queries

z = df.groupby(by = ['Sex','Age_Group']).count()

females = z.loc['F',:]
females['Age Group'] = females.index
f = females.copy()
f.index = [1,2,3,4,5,6,7,8,9,0,10,]
f.sort_index(inplace = True)

males = z.loc['M',:]
males['Age Group'] = males.index
m = males.copy()
m.index = [1,2,3,4,5,6,7,8,9,0,10,]
m.sort_index(inplace = True)

age_sex_bar = go.Figure(data = [
    go.Bar(name = 'M', x = m['Age Group'], y = m.HA, marker = dict(color = '#3D9BE9')),
    go.Bar(name = 'F', x = m['Age Group'], y = f.HA, marker = dict(color = '#3FE3D1'))
    ])
age_sex_bar.update_layout(
    barmode='stack',
    title = 'Age, Sex and COVID Cases',
    paper_bgcolor = 'white',
    plot_bgcolor = 'white',
    xaxis = dict(
        title  = 'Age Group'),
    yaxis = dict(
        title = 'COVID Cases')
    )

app.layout = html.Div([
    html.Div([
        html.H1("PROOF of CARE - B.C. COVID -19 Updates",)
    ]),
    html.Div(
        className = 'top_container',
        children = [
            html.Div(
                className ='boxes_container',
                children = [
                    html.Div(
                        className = "first_update_box",
                        children = [
                            html.P('Data Updated for: {}' .format(most_recent))
                    ]),
                    html.Div(
                        className = 'update_box',
                        children = [
                            html.P('Active Cases: {}' .format(BC_active_cases))]),
                    html.Div(
                        className = 'update_box',
                        children = [
                            html.P("Previous Day Cases: {}" .format(previous_covid_cases ))
                    ]),
                    html.Div(
                        className = "update_box",
                        children = [
                            html.P("Total Recovered: {}" .format(daily_df['Recovered Cases'].sum()))
                        ]
                    ),
                    html.Div(
                        className ='last_update_box',
                        children = [
                            html.P("Cases for Past 7 Days: {}" .format(one_week_trend))
                    ]),
            ], style = {'font-family':'Lucida Grande', 'font-weight':'bold',
                'font-size':18,'color':'#7d7d7d'}),
            html.Div(
                className = 'daily_cases_container',
                children = [
                    html.Button('Daily Cases', id = 'btn-nclicks-1', n_clicks=0, className ='Buttons'),
                    html.Button('7 Day Average', id = 'btn-nclicks-2', n_clicks=0, className = 'Buttons'),
                    html.Div(id = 'graphs_container')
            ]),
        ]),
    html.Div(
        className = "radioitem_container",
        children = [
            dcc.RadioItems(
                className = 'radioitem_active_total',
                id = 'active_total_radioitem',
                options = [{'label':i, 'value':i} for i in ['Active Cases', 'Total Cases', 'Recovered Cases']],
                value = 'Active Cases'),
        ]),
    html.Div(
        className = 'bot_graph_container',
        children = [
            html.Div(
                className = "active_total_container",
                children = [
                    dcc.Graph(
                        className = 'active_total_cases',
                        id = 'active_total_graph'),
                    ]),
            html.Div(
                className = "sex_age_container",
                children = [
                    dcc.Graph(
                        className = "sex_age",
                        figure = age_sex_bar
                        )
                    ]),
    ]),
    html.Div([
        html.A('@Proof of Care Inc', href = 'https://www.proofofcare.com/' ,style = {'color':'#01AEEF'}),
            html.Div([
                html.P("Sources from ", style = {'display':'inline'}),
                html.A("BC Centre for Disease Control", href = "http://www.bccdc.ca/health-info/diseases-conditions/covid-19/data",
                style = {'display':'inline','color':'#01AEEF'})])
    ], style = {'margin-right':'5%', 'float':'right'})
])

@app.callback(
    Output('graphs_container', 'children'),
    [Input('btn-nclicks-1', 'n_clicks'),
    Input('btn-nclicks-2', 'n_clicks')])

def button_output(btn1, btn2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn-nclicks-1' in changed_id:
        covid_graph = go.Figure(
            go.Scatter(
                x = pd.to_datetime(covid_count.index).sort_values(), y = covid_count.HA, name = 'Daily Cases', opacity = .8,
                    marker = dict(color='#01AEEF')))
        covid_graph.update_layout(
            title ="Daily Covid Cases in BC",
            paper_bgcolor = 'white',
            plot_bgcolor ='white',
            xaxis = dict(
                title = "Time",
            ),
            yaxis =dict(
                title = "Cases"),
        )

    elif 'btn-nclicks-2' in changed_id:
        covid_graph = go.Figure(
            go.Scatter(
                x = pd.to_datetime(covid_count.index).sort_values(), y = covid_count.HA.rolling(7).mean(), name = '7 Day Average',
                    opacity = 1, marker = dict(color = '#3D9BE9'))
                    )
        covid_graph.update_layout(
            title ="7 Day Covid Trend in BC",
            paper_bgcolor = 'white',
            plot_bgcolor ='white',
            xaxis = dict(
                title = "Time",
            ),
            yaxis =dict(
                title = "Cases"),
        )
    else:
        covid_graph = go.Figure(
            go.Scatter(
                x = pd.to_datetime(covid_count.index).sort_values(), y = covid_count.HA, name = 'Daily Cases', opacity = .8,
                    marker = dict(color='#01AEEF')))
        covid_graph.update_layout(
            title ="Daily Covid Cases in BC",
            paper_bgcolor = 'white',
            plot_bgcolor ='white',
            xaxis = dict(
                title = "Time",
            ),
            yaxis =dict(
                title = "Cases"),
        )
    return html.Div(dcc.Graph(figure = covid_graph))



@app.callback(
    Output('active_total_graph', 'figure'),
    [Input('active_total_radioitem', 'value')])

def active_total_graph_render(activeortotal):
    filtered_df = daily_df[['Health Authority',activeortotal]]
    fig = px.pie(filtered_df, values = activeortotal, names = 'Health Authority', hole = .4)
    fig.update_layout(
        title = (activeortotal + ' Region Distribution in BC')
    )
    return fig

if __name__ =='__main__':
    app.run_server(debug = True)





### end

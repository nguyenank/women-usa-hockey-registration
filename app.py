# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as colors
import pandas as pd
import numpy as np
import json
import time

from components import INDEX_STRING, getChoropleth, createTab


dfValue = pd.read_pickle("./data/girls-women-by-district-by-state.pkl")
df06 = pd.read_pickle("./data/pct_change_06-20.pkl")
dfAbsChange06 = pd.read_pickle("./data/abs_change_06-20.pkl")
df91 = pd.read_pickle("./data/pct_change_91-04.pkl")
dfAbsChange91 = pd.read_pickle("./data/abs_change_91-04.pkl")
with open("./data/states.geojson") as response:
    states = json.load(response)


# with open("./data/districts07-20.geojson") as response:
#     districts = json.load(response)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
app.title = "Girls/Women USA Hockey Enrollment"
app.index_string = INDEX_STRING

app.layout = html.Div(
    [
        dcc.Tabs(
            id="tabs-year",
            value="tab-06-20",
            children=[
                dcc.Tab(label="1991-2004", value="tab-91-04"),
                dcc.Tab(label="2006-2020", value="tab-06-20"),
            ],
            colors={
                "border": "#d6d6d6",
                "primary": "rgb(67,147,195)",
                "background": "#f9f9f9",
            },
        ),
        html.Div(id="tabs-year-content"),
    ]
)

### CALLBACKS

# Tab
@app.callback(Output("tabs-year-content", "children"), Input("tabs-year", "value"))
def render_tab(tab):
    return createTab(tab)


# Slider
@app.callback(
    [
        Output("interval-06", "max_intervals"),
        Output("interval-06", "n_intervals"),
    ],
    [
        Input("play-06", "n_clicks"),
        Input("pause-06", "n_clicks"),
        State("year-06", "value"),
    ],
    prevent_initial_call=True,
)
def button_06(play, pause, year):
    ctx = dash.callback_context
    if dash.callback_context.triggered[0]["prop_id"] == "play-06.n_clicks":
        if year == 2020:
            return (14, 0)
        return (2020 - year - 1, 0)
    else:
        return (0, 0)


@app.callback(
    Output("year-06", "value"),
    [Input("interval-06", "n_intervals"), State("year-06", "value")],
    prevent_initial_call=True,
)
def interval_update__06(n, year):
    if year == 2020:
        return 2006
    return year + 1


@app.callback(
    [
        Output("interval-91", "max_intervals"),
        Output("interval-91", "n_intervals"),
    ],
    [
        Input("play-91", "n_clicks"),
        Input("pause-91", "n_clicks"),
        State("year-91", "value"),
    ],
    prevent_initial_call=True,
)
def button_91(play, pause, year):
    ctx = dash.callback_context
    if dash.callback_context.triggered[0]["prop_id"] == "play-91.n_clicks":
        if year == 2004:
            return (13, 0)
        return (2004 - year - 1, 0)
    else:
        return (0, 0)


@app.callback(
    Output("year-91", "value"),
    [Input("interval-91", "n_intervals"), State("year-91", "value")],
    prevent_initial_call=True,
)
def interval_update_91(n, year):
    if year == 2004:
        return 1991
    return year + 1


# Choropleth


def abbrevToState(a):
    states = {
        "AL": "Alabama",
        "AK": "Alaska",
        "AZ": "Arizona",
        "AR": "Arkansas",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DC": "Washington, D.C.",
        "DE": "Delaware",
        "FL": "Florida",
        "GA": "Georgia",
        "HI": "Hawaii",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "IA": "Iowa",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "ME": "Maine",
        "MD": "Maryland",
        "MA": "Massachusetts",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MS": "Mississippi",
        "MO": "Missouri",
        "MT": "Montana",
        "NE": "Nebraska",
        "NV": "Nevada",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NY": "New York",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PA": "Pennsylvania",
        "E PA": "East Pennsylvania",
        "W PA": "West Pennsylvania",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VT": "Vermont",
        "VA": "Virginia",
        "WA": "Washington",
        "WV": "West Virginia",
        "WI": "Wisconsin",
        "WY": "Wyoming",
    }
    return f"{states[a]} ({a})"


@app.callback(
    Output("choropleth-06", "figure"),
    [Input("year-06", "value"), Input("ages-06", "value")],
)
def display_choropleth_06(year, ages):
    df = df06[df06.Year == str(year)].fillna(0).replace(np.inf, 99999.99)
    customdata = np.dstack(
        (
            list(df["State"].apply(abbrevToState)),
            dfValue[dfValue.Year == str(year)][ages],
            dfAbsChange06[dfAbsChange06.Year == str(year)][ages],
        )
    )[0]
    return getChoropleth(df["State"], df[ages], customdata, states, year)


@app.callback(
    Output("choropleth-91", "figure"),
    [Input("year-91", "value")],
)
def display_choropleth_91(year):
    df = df91[df91.Year == str(year)].fillna(0).replace(np.inf, 99999.99)
    customdata = np.dstack(
        (
            list(df["State"].apply(abbrevToState)),
            dfValue[dfValue.Year == str(year)].Total,
            dfAbsChange91[dfAbsChange91.Year == str(year)].Total,
        )
    )[0]
    return getChoropleth(df["State"], df.Total, customdata, False, year)


if __name__ == "__main__":
    app.run_server(debug=True)

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
dfDistrictsValue = pd.read_pickle("./data/districts/girls-women-by-district.pkl")
df06 = pd.read_pickle("./data/06-20/pct_change_06-20.pkl")
dfAbsChange06 = pd.read_pickle("./data/06-20/abs_change_06-20.pkl")

df91 = pd.read_pickle("./data/91-04/pct_change_91-04.pkl")
dfAbsChange91 = pd.read_pickle("./data/91-04/abs_change_91-04.pkl")

dfDistricts = pd.read_pickle("./data/districts/pct_change_districts.pkl")
dfAbsChangeDistricts = pd.read_pickle("./data/districts/abs_change_districts.pkl")

with open("./data/states.geojson") as response:
    states = json.load(response)

with open("./data/districts07-20.geojson") as response:
    districts = json.load(response)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

server = app.server

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
                dcc.Tab(label="Districts (2007-2020)", value="tab-districts"),
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
    return getChoropleth(
        **{
            "locations": df["State"],
            "z": df[ages],
            "customdata": customdata,
            "geojson": states,
            "year": year,
            "ages": ages,
            "zmax": 100,
            "zmin": -100,
        }
    )


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
    return getChoropleth(
        **{
            "locations": df["State"],
            "z": df.Total,
            "customdata": customdata,
            "geojson": False,
            "year": year,
            "ages": "",
            "zmax": 100,
            "zmin": -100,
        }
    )


@app.callback(
    Output("choropleth-district", "figure"),
    [Input("year-district", "value"), Input("ages-district", "value")],
)
def display_choropleth_district(year, ages):
    df = dfDistricts[dfDistricts.Year == str(year)].fillna(0).replace(np.inf, 99999.99)
    customdata = np.dstack(
        (
            list(df["District"]),
            dfDistrictsValue[dfDistrictsValue.Year == str(year)][ages],
            dfAbsChangeDistricts[dfAbsChangeDistricts.Year == str(year)][ages],
        )
    )[0]
    return getChoropleth(
        **{
            "locations": df["District"],
            "z": df[ages],
            "customdata": customdata,
            "geojson": districts,
            "year": year,
            "ages": ages,
            "zmax": 25,
            "zmin": -25,
        }
    )


if __name__ == "__main__":
    app.run_server(debug=True)

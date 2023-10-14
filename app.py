# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as colors
import pandas as pd
import numpy as np
import json
import time

from components import INDEX_STRING, getChoropleth, getAbsoluteChoropleth, createTab

##### Percent Change data
# District Data
dfDistrictsValue = pd.read_pickle(
    "./data/percent_change/districts/girls-women-by-district.pkl"
)
dfAbsChangeDistricts = pd.read_pickle(
    "./data/percent_change/districts/abs_change_districts.pkl"
)
dfDistricts = pd.read_pickle("./data/percent_change/districts/pct_change_districts.pkl")

# 1991 - 2022 State Data
dfValue = pd.read_pickle("./data/girls-women-by-district-by-state.pkl")

# 2006 -2022 Data
df06 = pd.read_pickle("./data/percent_change/06-22/pct_change_06-22.pkl")
dfAbsChange06 = pd.read_pickle("./data/percent_change/06-22/abs_change_06-22.pkl")

# 1991 - 2004 Data
df91 = pd.read_pickle("./data/percent_change/91-04/pct_change_91-04.pkl")
dfAbsChange91 = pd.read_pickle("./data/percent_change/91-04/abs_change_91-04.pkl")

# map of states (including East and West PA + Washington DC)
with open("./data/states.geojson") as response:
    states = json.load(response)

# map of USA Hockey districts from 2007 to 2022
with open("./data/districts07-22.geojson") as response:
    districts = json.load(response)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

server = app.server

app.title = "Girls/Women USA Hockey Registration"
app.index_string = INDEX_STRING  # format HTML

app.layout = html.Div(
    [
        dcc.Tabs(
            id="tabs-overall",
            value="tab-registration-numbers",
            children=[
                dcc.Tab(
                    label="Registration Numbers",
                    id="tab-registration-numbers",
                    value="subtab-registration-numbers",
                    children=[],
                ),
                dcc.Tab(
                    label="Percent Change",
                    id="tab-percent-change",
                    value="subtab-percent-change",
                    children=[],
                ),
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
subtab_style = {"height": "44px", "padding": "10px 25px"}


@app.callback(
    Output("tab-registration-numbers", "children"), [Input("tabs-overall", "value")]
)
def update_tabs(value):
    if value == "subtab-registration-numbers":
        return (
            dcc.Tabs(
                id="subtab-registration-numbers",
                value="tab-overall",
                children=[
                    dcc.Tab(
                        label="Overall (1990-2022)",
                        value="tab-overall",
                        style=subtab_style,
                        selected_style=subtab_style,
                    ),
                    dcc.Tab(
                        label="Age Group (2005-2022)",
                        value="tab-age-group",
                        style=subtab_style,
                        selected_style=subtab_style,
                    ),
                    dcc.Tab(
                        label="Districts (2005-2022)",
                        value="tab-abs-districts",
                        style=subtab_style,
                        selected_style=subtab_style,
                    ),
                ],
            ),
        )


@app.callback(
    Output("tab-percent-change", "children"), [Input("tabs-overall", "value")]
)
def update_tabs(value):
    if value == "subtab-percent-change":
        return (
            dcc.Tabs(
                id="subtab-percent-change",
                value="tab-06-22",
                children=[
                    dcc.Tab(
                        label="States (1991-2004)",
                        value="tab-91-04",
                        style=subtab_style,
                        selected_style=subtab_style,
                    ),
                    dcc.Tab(
                        label="States (2006-2022)",
                        value="tab-06-22",
                        style=subtab_style,
                        selected_style=subtab_style,
                    ),
                    dcc.Tab(
                        label="Districts (2008-2022)",
                        value="tab-districts",
                        style=subtab_style,
                        selected_style=subtab_style,
                    ),
                ],
            ),
        )


# Tab
@app.callback(
    Output("tabs-year-content", "children", allow_duplicate=True),
    Input("subtab-percent-change", "value"),
    prevent_initial_call="initial_duplicate",
)
def render_tab(tab):
    return createTab(tab)


@app.callback(
    Output("tabs-year-content", "children"),
    Input("subtab-registration-numbers", "value"),
)
def render_tab(tab):
    return createTab(tab)


# Choropleth


def abbrevToState(a):
    """
    convert state abbreviation to the full name
    """

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
    # customdata is for additional info in the hover
    customdata = np.dstack(
        (
            list(df["State"].apply(abbrevToState)),
            dfValue[dfValue.Year == str(year)][ages],
            dfAbsChange06[dfAbsChange06.Year == str(year)][ages],
        )
    )[0]
    total = np.sum(dfValue[dfValue.Year == str(year)][ages])
    lastYearTotal = np.sum(dfValue[dfValue.Year == str(year - 1)][ages])
    overall_change = (total - lastYearTotal) / lastYearTotal * 100
    return getChoropleth(
        **{
            "locations": df["State"],
            "z": df[ages],
            "customdata": customdata,
            "geojson": states,
            "year": year,
            "ages": ages,
            "overall_change": overall_change,
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
    # customdata is for additional info in the hover
    customdata = np.dstack(
        (
            list(df["State"].apply(abbrevToState)),
            dfValue[dfValue.Year == str(year)].Total,
            dfAbsChange91[dfAbsChange91.Year == str(year)].Total,
        )
    )[0]
    total = np.sum(dfValue[dfValue.Year == str(year)].Total)
    lastYearTotal = np.sum(dfValue[dfValue.Year == str(year - 1)].Total)
    overall_change = (total - lastYearTotal) / lastYearTotal * 100
    return getChoropleth(
        **{
            "locations": df["State"],
            "z": df.Total,
            "customdata": customdata,
            "geojson": False,  # before 07, just uses normal states layout
            "year": year,
            "ages": "",
            "overall_change": overall_change,
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
    # customdata is for additional info in the hover
    customdata = np.dstack(
        (
            list(df["District"]),
            dfDistrictsValue[dfDistrictsValue.Year == str(year)][ages],
            dfAbsChangeDistricts[dfAbsChangeDistricts.Year == str(year)][ages],
        )
    )[0]
    total = np.sum(dfDistrictsValue[dfDistrictsValue.Year == str(year)][ages])
    lastYearTotal = np.sum(
        dfDistrictsValue[dfDistrictsValue.Year == str(year - 1)][ages]
    )
    overall_change = (total - lastYearTotal) / lastYearTotal * 100
    return getChoropleth(
        **{
            "locations": df["District"],
            "z": df[ages],
            "customdata": customdata,
            "geojson": districts,
            "year": year,
            "ages": ages,
            "overall_change": overall_change,
            "zmax": 25,
            "zmin": -25,
        }
    )


@app.callback(
    Output("choropleth-overall", "figure"),
    [Input("year-overall", "value")],
)
def display_choropleth_overall(year):
    df = dfValue[dfValue.Year == str(year)].fillna(0).replace(np.inf, 99999.99)
    # customdata is for additional info in the hover
    customdata = np.dstack(
        (
            list(df["State"].apply(abbrevToState)),
            dfValue[dfValue.Year == str(year)].Total,
        )
    )[0]
    total = np.sum(dfValue[dfValue.Year == str(year)].Total)
    return getAbsoluteChoropleth(
        **{
            "locations": df["State"],
            "z": df.Total,
            "customdata": customdata,
            "geojson": states,  # switches over in year == 2005
            "year": year,
            "ages": "",
            "total": total,
            "zmax": 4000,
            "zmin": 0,
        }
    )


@app.callback(
    Output("choropleth-age-group", "figure"),
    [Input("year-age-group", "value"), Input("ages-age-group", "value")],
)
def display_choropleth_age_group(year, ages):
    df = dfValue[dfValue.Year == str(year)].fillna(0).replace(np.inf, 99999.99)
    # customdata is for additional info in the hover
    customdata = np.dstack(
        (
            list(df["State"].apply(abbrevToState)),
            dfValue[dfValue.Year == str(year)][ages],
        )
    )[0]
    total = np.sum(dfValue[dfValue.Year == str(year)][ages])
    return getAbsoluteChoropleth(
        **{
            "locations": df["State"],
            "z": df[ages],
            "customdata": customdata,
            "geojson": states,  # switches over in year == 2005
            "year": year,
            "ages": ages,
            "total": total,
            "zmax": 500,
            "zmin": 0,
        }
    )


@app.callback(
    Output("choropleth-abs-district", "figure"),
    [Input("year-abs-district", "value"), Input("ages-abs-district", "value")],
)
def display_choropleth_district(year, ages):
    df = (
        dfDistrictsValue[dfDistrictsValue.Year == str(year)]
        .fillna(0)
        .replace(np.inf, 99999.99)
    )
    # customdata is for additional info in the hover
    customdata = np.dstack(
        (
            list(df["District"]),
            dfDistrictsValue[dfDistrictsValue.Year == str(year)][ages],
        )
    )[0]
    total = np.sum(dfDistrictsValue[dfDistrictsValue.Year == str(year)][ages])
    return getAbsoluteChoropleth(
        **{
            "locations": df["District"],
            "z": df[ages],
            "customdata": customdata,
            "geojson": districts,
            "year": year,
            "ages": ages,
            "total": total,
            "zmax": 15000,
            "zmin": 0,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)

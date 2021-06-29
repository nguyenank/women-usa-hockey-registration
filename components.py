from functools import reduce
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as colors
import pandas as pd
import numpy as np
import json
import time

INDEX_STRING = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;700&display=swap" rel="stylesheet">
    </head>
    <body>
        {%app_entry%}
        <footer>
            <hr />
            <div class="container">
                Created by An Nguyen (twitter: @nguyenank_). Data taken from USA Hockey.
            </div>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""


def flattenDictionary(d):
    """
    flatten a list of dicts into one dict
    """

    def f(x, y):
        x.update(y)
        return x

    return reduce(f, d)


def getColor(percent):
    c = colors.diverging.RdBu
    shift = percent + 100
    if shift > 199:
        shift = 199
    elif shift < 0:
        shift = 0
    elif shift > 100 and shift < 120:
        shift = 120
    index = round((shift) / 20)
    return c[index]


def createSlider(minYear, maxYear, suffix):
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Center(
                                    html.Button("Play", id="play" + suffix, n_clicks=0)
                                ),
                                html.Button("Pause", id="pause" + suffix, n_clicks=0),
                            ]
                        ),
                        width=1,
                    ),
                    dbc.Col(
                        dcc.Slider(
                            id="year" + suffix,
                            step=None,
                            min=minYear,
                            max=maxYear,
                            marks=flattenDictionary(
                                [{x: str(x)} for x in range(minYear, maxYear + 1)]
                            ),
                            value=maxYear,
                        ),
                        align="end",
                    ),
                ],
            ),
            dcc.Interval(
                id="interval" + suffix,
                interval=2000,
                max_intervals=maxYear - minYear,
                n_intervals=maxYear - minYear,
            ),
        ]
    )


def createTab(tab):
    if tab == "tab-06-20":
        return dbc.Container(
            html.Div(
                [
                    html.H3(
                        children="Percent Change in USA Hockey Enrollment for Girls/Women (2006-2020)"
                    ),
                    html.Label("Age Group"),
                    dcc.Dropdown(
                        clearable=False,
                        options=[
                            {"label": x, "value": x}
                            for x in [
                                "Total",
                                "20&Over",
                                "19",
                                "17-18",
                                "15-16",
                                "13-14",
                                "11-12",
                                "9-10",
                                "7-8",
                                "6&U",
                            ]
                        ],
                        value="Total",
                        id="ages-06",
                    ),
                    dcc.Graph(
                        id="choropleth-06",
                        config={"displayModeBar": False, "scrollZoom": False},
                    ),
                    createSlider(2006, 2020, "-06"),
                ],
            )
        )
    elif tab == "tab-91-04":
        return dbc.Container(
            html.Div(
                [
                    html.H3(
                        children="Percent Change in USA Hockey Enrollment for Girls/Women (1991-2004)"
                    ),
                    dcc.Graph(
                        id="choropleth-91",
                        config={"displayModeBar": False, "scrollZoom": False},
                    ),
                    createSlider(1991, 2004, suffix="-91"),
                ]
            )
        )


def getChoropleth(locations, z, customdata, geojson, year):
    choropleth = go.Choropleth(
        colorscale="RdBu",
        colorbar={
            "ticksuffix": "%",
            "tickfont": {"family": "Public Sans"},
            "title": {
                "font": {"family": "Public Sans"},
                "side": "right",
                "text": "<b>Percent Change</b>",
            },
        },
        hoverlabel={
            "bgcolor": list(z.apply(getColor)),
            "font": {"family": "Public Sans"},
        },
        geojson=geojson,
        locations=locations,
        featureidkey="properties.Name",
        z=z,
        zmax=100,
        zmin=-100,
        zmid=0,
        marker_line_color="white",
        customdata=customdata,
        hovertemplate="<em>%{customdata[0]}</em>"
        + "<br><b>% Change:</b> %{z:.2f}%</br>"
        + "<b>Number:</b> %{customdata[1]:,}"
        + "<br><b># Change:</b> %{customdata[2]:+,}</br><extra></extra>",
    )
    if not geojson:
        choropleth.locationmode = "USA-states"
    fig = go.Figure(choropleth)
    fig.update_geos(scope="usa")
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 1, "b": 0},
        title={
            "font": {"family": "Public Sans"},
            "text": f"<b>{year}</b>",
            "x": 0.85,
            "y": 0.1,
            "yanchor": "bottom",
        },
    )
    return fig

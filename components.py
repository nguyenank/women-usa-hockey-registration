from functools import reduce
from math import ceil, floor
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as colors
import pandas as pd
import numpy as np
import json
import time

# HTML Layout
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
        <script defer data-domain="women-usa-hockey-registration-422d1425d167.herokuapp.com" src="https://plausible.io/js/script.js"></script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            <hr />
            <div class="container">
                Created by An Nguyen (bluesky: nguyenank@bsky.social). Data taken from USA Hockey.
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


def getDivergingColor(percent, range):
    """
    approximately get appropriate color on scale for hover background
    """
    c = colors.diverging.RdBu
    if percent == 0:
        return c[len(c) // 2 + 1]
    # exclude halfway point from color scale
    c = c[: len(c) // 2 + 1] + c[len(c) // 2 + 2 :]
    div_factor = range / len(c)
    shift = percent + range / 2
    # prevent out of bounds indexing
    if shift > range - 1:
        shift = range - 1
    elif shift < 0:
        shift = 0
    low_index = floor(shift / div_factor)
    if low_index == len(c) - 1:  # get maximum color
        return c[low_index]
    return colors.label_rgb(  # find color proportionally in between
        colors.find_intermediate_color(
            colors.unlabel_rgb(c[low_index]),
            colors.unlabel_rgb(c[low_index + 1]),
            shift / div_factor - low_index,
        )
    )


def getAbsoluteColor(value, range):
    """
    approximately get appropriate color on scale for hover background
    """
    c = colors.sequential.Blues
    percent = value / range
    if percent > 1:
        return c[len(c) - 1]
    val = (len(c) - 1) * percent
    low_index = floor(val)
    return colors.label_rgb(  # find color proportionally in between
        colors.find_intermediate_color(
            colors.unlabel_rgb(c[low_index]),
            colors.unlabel_rgb(c[low_index + 1]),
            val - low_index,
        )
    )


def createSlider(minYear, maxYear, suffix):
    return dcc.Slider(
        id="year" + suffix,
        step=None,
        min=minYear,
        max=maxYear,
        marks=flattenDictionary([{x: str(x)} for x in range(minYear, maxYear + 1)]),
        value=maxYear,
    )


def createTab(tab):
    if tab == "tab-06-22":
        return dbc.Container(
            html.Div(
                [
                    html.H3(
                        children="Percent Change in USA Hockey Registration for Girls/Women (2006-2022)"
                    ),
                    html.Label("Age Group"),
                    dcc.Dropdown(
                        clearable=False,
                        options=[
                            {"label": x if x != "Total" else "All Ages", "value": x}
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
                    createSlider(2006, 2022, "-06"),
                ],
            )
        )
    elif tab == "tab-91-04":
        return dbc.Container(
            html.Div(
                [
                    html.H3(
                        children="Percent Change in USA Hockey Registration for Girls/Women (1991-2004)"
                    ),
                    dcc.Graph(
                        id="choropleth-91",
                        config={"displayModeBar": False, "scrollZoom": False},
                    ),
                    createSlider(1991, 2004, suffix="-91"),
                ]
            )
        )
    elif tab == "tab-districts":
        return dbc.Container(
            html.Div(
                [
                    html.H3(
                        children="Percent Change in USA Hockey Registration for Girls/Women by District (2008-2022)"
                    ),
                    html.Label("Age Group"),
                    dcc.Dropdown(
                        clearable=False,
                        options=[
                            {"label": x if x != "Total" else "All Ages", "value": x}
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
                        id="ages-district",
                    ),
                    dcc.Graph(
                        id="choropleth-district",
                        config={"displayModeBar": False, "scrollZoom": False},
                    ),
                    createSlider(2008, 2022, "-district"),
                ],
            )
        )
    elif tab == "tab-overall":
        return dbc.Container(
            html.Div(
                [
                    html.H3(
                        children="Overall USA Hockey Registration for Girls/Women (1990-2022)"
                    ),
                    dcc.Graph(
                        id="choropleth-overall",
                        config={"displayModeBar": False, "scrollZoom": False},
                    ),
                    createSlider(1990, 2022, suffix="-overall"),
                ],
            )
        )
    elif tab == "tab-age-group":
        return dbc.Container(
            html.Div(
                [
                    html.H3(
                        children="Overall USA Hockey Registration for Girls/Women by Age Group (2005-2022)"
                    ),
                    html.Label("Age Group"),
                    dcc.Dropdown(
                        clearable=False,
                        options=[
                            {"label": x if x != "Total" else "All Ages", "value": x}
                            for x in [
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
                        value="20&Over",
                        id="ages-age-group",
                    ),
                    dcc.Graph(
                        id="choropleth-age-group",
                        config={"displayModeBar": False, "scrollZoom": False},
                    ),
                    createSlider(2005, 2022, suffix="-age-group"),
                ],
            )
        )
    elif tab == "tab-abs-districts":
        return dbc.Container(
            html.Div(
                [
                    html.H3(
                        children="Overall USA Hockey Registration for Girls/Women by District (2007-2022)"
                    ),
                    html.Label("Age Group"),
                    dcc.Dropdown(
                        clearable=False,
                        options=[
                            {"label": x if x != "Total" else "All Ages", "value": x}
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
                        id="ages-abs-district",
                    ),
                    dcc.Graph(
                        id="choropleth-abs-district",
                        config={"displayModeBar": False, "scrollZoom": False},
                    ),
                    createSlider(2007, 2022, suffix="-abs-district"),
                ],
            )
        )


def getChoropleth(
    locations, z, customdata, geojson, year, ages, overall_change, zmax, zmin
):
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
            "bgcolor": list(z.apply(getDivergingColor, args=(zmax - zmin,))),
            "font": {"family": "Public Sans"},
        },
        geojson=geojson,
        locations=locations,
        featureidkey="properties.Name",  # matching property in geojson
        z=z,
        zmax=zmax,
        zmin=zmin,
        zmid=0,
        marker_line_color="white",
        customdata=customdata,
        hovertemplate="<em>%{customdata[0]}</em>"
        + "<br><b>% Change:</b> %{z:.2f}%</br>"
        + "<b># Players:</b> %{customdata[1]:,}"
        + "<br><b># Change:</b> %{customdata[2]:+,}</br><extra></extra>",
    )
    if not geojson:  # no geojson, use default states
        choropleth.locationmode = "USA-states"
    fig = go.Figure(choropleth)
    fig.update_geos(scope="usa")
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 1, "b": 0},
        title={
            "font": {"family": "Public Sans"},
            "text": f"<br><b>{year}</b></br><b>{ages if ages != 'Total' else 'All Ages'}</b><br /> <br /><b>Overall Percent Change</b>:</br><b>{overall_change:.2f}</b>%",
            "x": 0.80,
            "y": 0.3,
            "yanchor": "bottom",
        },
        dragmode=False,
    )
    return fig


def getAbsoluteChoropleth(
    locations, z, customdata, geojson, year, ages, total, zmax, zmin
):
    if geojson:
        geojson = False if year < 2005 else geojson

    choropleth = go.Choropleth(
        colorscale="Blues",
        colorbar={
            "tickfont": {"family": "Public Sans"},
            "title": {
                "font": {"family": "Public Sans"},
                "side": "right",
                "text": "<b>Number of Registrations</b>",
            },
        },
        hoverlabel={
            "bgcolor": list(z.apply(getAbsoluteColor, args=((zmax - zmin),))),
            "font": {"family": "Public Sans"},
        },
        geojson=geojson,
        locations=locations,
        featureidkey="properties.Name",  # matching property in geojson
        z=z,
        zmax=zmax,
        zmin=zmin,
        marker_line_color="white",
        customdata=customdata,
        hovertemplate="<em>%{customdata[0]}</em>"
        + "<br><b># Players:</b> %{customdata[1]:,}</br><extra></extra>",
    )
    if not geojson:  # no geojson, use default states
        choropleth.locationmode = "USA-states"
    fig = go.Figure(choropleth)
    fig.update_geos(scope="usa")
    fig.update_layout(
        dragmode=False,
        margin={"r": 0, "t": 0, "l": 1, "b": 0},
        title={
            "font": {"family": "Public Sans"},
            "text": f"<b>{year}</b><br /><b>{ages if ages != 'Total' else 'All Ages'}</b><br /><br></br><b>{total} Registrations</b>"
            if ages
            else f"<br><b>{year}</b></br><br /><b>{total} Registrations</b>",
            "x": 0.80,
            "y": 0.3,
            "yanchor": "bottom",
        },
    )
    return fig

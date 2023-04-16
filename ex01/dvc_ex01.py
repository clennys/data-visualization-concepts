# -*- coding: utf-8 -*-
"""DVC_ex01.ipynb

"""

import pandas as pd
from bokeh.plotting import figure
from bokeh.io import output_file, save, show, output_notebook
from bokeh.models import ColumnDataSource, HoverTool, FactorRange, NumeralTickFormatter
from bokeh.layouts import gridplot
from bokeh.transform import factor_cmap
from bokeh.models.annotations import Label
from bokeh.palettes import Blues
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdNgN-88U31tk1yQytaJdmoLrxuFn1LnbwTubwCd8se2aHh8656xLLHzxHSoiaXMUu8rIcu6gMj5Oq/pub?gid=1242961990&single=true&output=csv"
MAGMA_financials = pd.read_csv(url)

subset = ["Net Income", "Revenue", "Cost of Revenue"]

years = ["2019", "2020", "2021", "2022"]
quarters = ["Q1", "Q2", "Q3", "Q4"]
x = []
for y in years:
    for q in quarters:
        for s in subset:
            x.append((y, q, s))


def create_source(symbol):
    data = MAGMA_financials[MAGMA_financials.Symbol == symbol][subset]

    y = data.stack().values

    x_label = subset * 16

    return ColumnDataSource(data=dict(x=x, y=y, label=x_label))


symbols = MAGMA_financials.Symbol.unique()
sources = {symbol: create_source(symbol) for symbol in symbols}

options = dict(width=1000, height=500, tools="")


def draw_bar_chart(symbol):
    p = figure(x_range=FactorRange(*x), title=symbol, **options)

    p.xgrid.grid_line_color = None

    p.x_range.range_padding = 0.1

    p.xaxis.major_label_text_font_size = "0pt"

    p.xaxis.major_tick_line_color = None

    p.yaxis.axis_label = "millions USD"

    p.yaxis.formatter = NumeralTickFormatter(format="($ 0,0 a)")

    p.vbar(
        x="x",
        top="y",
        width=0.8,
        source=sources[symbol],
        legend_group="label",
        line_color="white",
        fill_color=factor_cmap("x", palette=Blues[3], factors=subset, start=2, end=3),
    )

    p.add_tools(
        HoverTool(
            tooltips=[
                ("(year, quarter, type = value)", "(@x = @y)"),
            ]
        )
    )

    p.legend.label_text_font_size = "11pt"
    p.legend.label_height = 10
    p.legend.glyph_height = 7
    p.legend.glyph_width = 20

    p.legend.orientation = "horizontal"
    p.legend.location = "top_right"
    p.output_backend = "svg"

    return p


def make_label(time, number):
    label = Label(
        x=500,
        y=100,
        x_units="screen",
        y_units="screen",
        text=f"{time}\nlayoffs\n{number}",
        text_font_size="10pt",
        text_font_style="bold",
        text_color="black",
        text_align="center",
        background_fill_color="white",
        background_fill_alpha=0.8,
    )

    return label


if __name__ == "__main__":
    p_AMZN = draw_bar_chart("AMZN")
    p_META = draw_bar_chart("META")
    p_GOOGL = draw_bar_chart("GOOGL")
    p_MSFT = draw_bar_chart("MSFT")

    labels = {
        "AMZN": make_label("Jan 2023", "18,000"),
        "META": make_label("Nov 2022", "11,000"),
        "GOOGL": make_label("Jan 2023", "12,000"),
        "MSFT": make_label("Jan 2023", "10,000"),
    }


    p_AMZN = draw_bar_chart("AMZN")
    p_AMZN.add_layout(labels["AMZN"])

    p_META = draw_bar_chart("META")
    p_META.add_layout(labels["META"])

    p_GOOGL = draw_bar_chart("GOOGL")
    p_GOOGL.add_layout(labels["GOOGL"])

    p_MSFT = draw_bar_chart("MSFT")
    p_MSFT.add_layout(labels["MSFT"])


    p = gridplot([[p_AMZN, None], [p_META, None], [p_GOOGL, None], [p_MSFT, None]], toolbar_location=None)

    output_file("dvc_ex1.html")
    save(p)
    show(p)

# -*- coding: utf-8 -*-
"""DVC_ex02.ipynb
"""

import pandas as pd
from bokeh.plotting import figure
from bokeh.io import output_file, save, show, output_notebook
from bokeh.layouts import column
from bokeh.models import (
    ColumnDataSource,
    CDSView,
    BooleanFilter,
    HoverTool,
    LinearAxis,
    NumeralTickFormatter,
    Range1d,
    RangeTool,
)

# Task 1: Prepare the Data
stock_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTiM1scE44za7xyuheW_FrUkdSdOKipDgDOWa_03ixmJCWK_ReSqhjzax66nNHyDKARXWIXgFI_EW9X/pub?gid=1661368486&single=true&output=csv"
stock = pd.read_csv(stock_url)

metrics_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRDaf4y17OWjQqxODuxA4q4hsvXRkSqN0na1KtTIpvOZUdc7xHbrkhcygFfDIyVQWI2UbC3YcKUbser/pub?gid=981872466&single=true&output=csv"
metrics = pd.read_csv(metrics_url)

## 1.1: Convert the data type of time columns to datetime using to_datatime()
stock["Date"] = pd.to_datetime(stock["Date"])
metrics["Quarter Ended"] = pd.to_datetime(metrics["Quarter Ended"])

# Define a function that create a candlestick chart for a company
def create_candlestick_chart(symbol):

    ## 2.1 Create the data source and set the basic properties of the figure

    # Use ColumnDataSource to create the data source
    # The dataframe is not directly used as source here
    # because you'll use CDSView filter later
    # which works with ColumnDataSource
    data_stock = stock[stock.Symbol == symbol]
    source = ColumnDataSource(data_stock)

    p = figure(
        width=800,
        height=400,
        title=symbol,
        # Specify the x range to be (min date, max date)
        # so that you can refer to this range in other plots
        x_range=(data_stock["Date"].min(), data_stock["Date"].max()),
        # Set the x axis to show date time
        x_axis_type="datetime",
        # Put the x axis to be at the top of the plot
        x_axis_location="above",
        background_fill_color="#fbfbfb",
        tools="pan,wheel_zoom,box_zoom,reset, save",
        toolbar_location="right",
    )

    p.xgrid.grid_line_color = "#e5e5e5"
    p.ygrid.grid_line_alpha = 0.5
    p.xaxis.major_label_text_font_size = "10px"
    p.yaxis.axis_label = "Stock Price in USD"
    p.yaxis.formatter = NumeralTickFormatter(format="(0.0a)")

    ## 2.2: Manually set the y axis range

    # Make it larger than the (min, max) range of the data
    # e.g. (min * 0.9, max * 1.1)
    # https://docs.bokeh.org/en/3.0.3/docs/reference/models/ranges.html#bokeh.models.DataRange1d
    p.y_range.start = data_stock.Low.min() * 0.9
    p.y_range.end = data_stock.High.max() * 1.1

    ## 2.3: Use CDSView to create two filters on the stock data

    # 'inc' keeps the data where the close price is higher than the open price
    # 'dec' does the opposite of 'inc'
    # https://docs.bokeh.org/en/latest/docs/user_guide/basic/data.html#filtering-data
    inc_bf = BooleanFilter(
        [True if row["Close"] > row["Open"] else False for _, row in data_stock.iterrows()]
    )
    dec_bf = BooleanFilter(
        [True if row["Close"] < row["Open"] else False for _, row in data_stock.iterrows()]
    )
    inc_view = CDSView(filter=inc_bf)
    dec_view = CDSView(filter=dec_bf)

    # Deprecated
    # inc = source.data["Close"] > source.data["Open"]
    # dec = source.data["Close"] < source.data["Open"]
    #
    # inc_view = CDSView(source=source, filters=[BooleanFilter(inc)])
    # dec_view = CDSView(source=source, filters=[BooleanFilter(dec)])

    ## 2.4: Draw the glyphs in the candlesticks

    # A candlestick consists of a segment and a vbar

    # Set the width of the vbar
    # Note that the unit of datetime axis is milliseconds
    # while the interval of the stock data is week

    # w = 6.048e+8 # 7 Days in ms
    w = 5.616e8  # 6.5 Days in ms for a cleaner look. Candles are separate when you zoom in.

    # Draw the segement and the vbar
    # inc vbars are green, dec vbars are red
    stock_segment = p.segment(
        x0="Date", x1="Date", y0="High", y1="Low", width=2, color="black", source=source
    )

    stock_inc = p.vbar(
        x="Date",
        width=w,
        top="Open",
        bottom="Close",
        fill_color="green",
        line_color="green",
        name="price",
        source=source,
        view=inc_view,
    )

    stock_dec = p.vbar(
        x="Date",
        width=w,
        top="Open",
        bottom="Close",
        fill_color="red",
        line_color="red",
        name="price",
        source=source,
        view=dec_view,
    )

    ## 2.5: Add volume bars in the candlestick chart

    # Note that volume data is different from stock price data in unit and scale
    # You'll create a twin y axis for volume on the right side of the chart
    # https://docs.bokeh.org/en/3.0.2/docs/user_guide/basic/axes.html#twin-axes
    # https://docs.bokeh.org/en/latest/docs/reference/models/axes.html#bokeh.models.LinearAxis

    y_volume = data_stock.Volume
    p.extra_y_ranges["volume"] = Range1d(start=y_volume.min()*0.9, end=y_volume.max()*1.1)

    y_volume_axis = LinearAxis(
        y_range_name="volume",
        axis_label="Volume",
        formatter=NumeralTickFormatter(format="0.0a"),
    )

    p.add_layout(y_volume_axis, "right")

    stock_volume = p.vbar(
        source=source,
        x="Date",
        y_range_name="volume",
        top="Volume",
        width=4,
        alpha=0.2,
        line_color="grey",
    )

    ## 2.6: Add a hover tool for the candlesticks

    # https://stackoverflow.com/questions/61175554/how-to-get-bokeh-hovertool-working-for-candlesticks-chart
    hover_stock = HoverTool()
    hover_stock.tooltips = [
        ("Date", "@Date{%Y-%m-%d}"),
        ("Open", "@Open{($0.00)}"),
        ("Close", "@Close{($0.00)}"),
        ("High", "@High{($0.00)}"),
        ("Low", "@Low{($0.00)}"),
        ("Volume", "@Volume{($0.00a)}"),
    ]

    # printf in order to show float numbers
    hover_stock.formatters = {
        "@Date": "datetime",
    }

    # This hover tool only shows tooltips on the vbars in the candlesticks, thus you need to specify the renderers
    hover_stock.renderers = [stock_inc, stock_dec]
    p.add_tools(hover_stock)

    p.output_backend = "svg"

    return p


# Task 3: Add Metrics Plot to the Candlestick Chart


def add_metrics_plot(main_plot):

    p = main_plot
    symbol = p.title.text

    # See how bokeh deals with data source containing nan values
    # https://docs.bokeh.org/en/latest/docs/user_guide/basic/lines.html#missing-points
    # Note that this might not work if the source is created from ColumnDataSource
    data_metrics = metrics[metrics.Symbol == symbol]
    source = ColumnDataSource(data_metrics)

    ## 3.1: Set the y axes for the metrics

    # 'PE Ration' and 'EPS Growth' also have different units from the stock price
    # You'll set a y axis for each metric
    # and make the extra y axes invisible
    y_pe = source.data["PE Ratio"]
    y_eps = source.data["EPS Growth"]

    p.extra_y_ranges["pe"] = Range1d(y_pe.min() * 1.0, y_pe.max() * 1.15)
    p.extra_y_ranges["eps"] = Range1d(y_eps.min() * 2.25, y_eps.max() * 1.1)

    y_pe_axis = LinearAxis(y_range_name="pe", visible=False)

    y_eps_axis = LinearAxis(y_range_name="eps", visible=False)

    ## 3.2 Use scatter and line glyphs to plot the metrics
    pe_l = p.line(
        source=source,
        x="Quarter Ended",
        y="PE Ratio",
        y_range_name="pe",
        legend_label="PE Ratio",
        line_color="grey",
    )

    pe_c = p.circle(
        source=source,
        x="Quarter Ended",
        y="PE Ratio",
        y_range_name="pe",
        legend_label="PE Ratio",
        line_color="grey",
        fill_color="grey",
        line_width=1,
    )

    eps_l = p.line(
        source=source,
        x="Quarter Ended",
        y="EPS Growth",
        y_range_name="eps",
        legend_label="EPS Growth",
        line_color="grey",
        line_dash = "dotted"
    )

    eps_c = p.circle(
        source=source,
        y_range_name="eps",
        x="Quarter Ended",
        y="EPS Growth",
        legend_label="EPS Growth",
        line_color="grey",
        fill_color="white",
        line_width=1,
    )
    ## 3.3: Make the legend of metrics interactive

    # Click on a legend to mute the corresponding glyph(s)
    # https://docs.bokeh.org/en/latest/docs/user_guide/interaction/legends.html#hiding-glyphs
    p.legend.click_policy = "mute"

    # Set the attributes of the legend to adjust its postion, color and size
    # https://docs.bokeh.org/en/latest/docs/reference/models/annotations.html#bokeh.models.Legend
    p.legend.location = "top_left"
    p.legend.orientation = "horizontal"
    p.legend.background_fill_alpha = 0
    p.legend.border_line_alpha = 0
    p.legend.label_text_font_size = "10px"
    p.legend.glyph_width = 16

    ## 3.4: Add a hovertool for the scatter glyphs

    metrics_hover = HoverTool()
    metrics_hover.tooltips = [
        ("Quarter Ended", "@{Quarter Ended}{%Y-%m-%d}"),
        ("PE Ratio", "@{PE Ratio}"),
        ("EPS Growth", "@{EPS Growth}"),
    ]
    metrics_hover.formatters = {
        "@{Quarter Ended}": "datetime",
    }
    metrics_hover.mode = "mouse"
    metrics_hover.renderers = [pe_c, eps_c]
    p.add_tools(metrics_hover)

    return p


if __name__ == "__main__":
    p = create_candlestick_chart("AAPL")
    p = add_metrics_plot(p)
    # p = add_select_range(p)
    output_file("dvc_ex2.html")
    save(p)
    show(p)

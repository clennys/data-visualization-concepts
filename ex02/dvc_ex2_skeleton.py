# Activate the proper environment
# Import necessary dependencies

import pandas as pd
from bokeh.plotting import figure 
from bokeh.io import output_file, save
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, CDSView, BooleanFilter, \
    HoverTool, LinearAxis, NumeralTickFormatter, Range1d, RangeTool
    
# Task 1: Prepare the Data

# The weekly stock data of META, AAPL, GOOGL, MSFT, AMZN (MAGMA) from 1/1/2019 to 27/12/2022
stock_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTiM1scE44za7xyuheW_FrUkdSdOKipDgDOWa_03ixmJCWK_ReSqhjzax66nNHyDKARXWIXgFI_EW9X/pub?gid=1661368486&single=true&output=csv'
stock = pd.read_csv(stock_url)

# The financial metrics 'PE Ratio' and 'EPS Growth' of MAGMA from 2019 Q1 to 2022 Q4
metrics_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRDaf4y17OWjQqxODuxA4q4hsvXRkSqN0na1KtTIpvOZUdc7xHbrkhcygFfDIyVQWI2UbC3YcKUbser/pub?gid=981872466&single=true&output=csv'
metrics = pd.read_csv(metrics_url)

## 1.1: Convert the data type of time columns to datetime using to_datatime()

# Column 'Date' in stock and column 'Quarter Ended' in metrics
stock['Date'] = ...
metrics['Quarter Ended'] = ...


# Task 2: Create A Candlestick Chart From the Stock Data

# https://docs.bokeh.org/en/latest/docs/user_guide/topics/timeseries.html#candlestick-chart

# Define a function that create a candlestick chart for a company 
def create_candlestick_chart(symbol):
    
    ## 2.1 Create the data source and set the basic properties of the figure

    # Use ColumnDataSource to create the data source
    # The dataframe is not directly used as source here
    # because you'll use CDSView filter later
    # which works with ColumnDataSource
    source = ...
    
    p = figure(
        width=800, 
        height=400, 
        title=symbol, 
        # Specify the x range to be (min date, max date)
        # so that you can refer to this range in other plots
        x_range=...,
        # Set the x axis to show date time
        x_axis_type=..., 
        # Put the x axis to be at the top of the plot
        x_axis_location= ...,
        background_fill_color = '#fbfbfb',
        tools=..., 
        toolbar_location='right',
    )
    
    p.xgrid.grid_line_color='#e5e5e5'
    p.ygrid.grid_line_alpha=0.5
    p.xaxis.major_label_text_font_size = '10px'
    p.yaxis.axis_label = 'Stock Price in USD'
    p.yaxis.formatter = ...
    
    ## 2.2: Manually set the y axis range 
    
    # Make it larger than the (min, max) range of the data
    # e.g. (min * 0.9, max * 1.1)
    # https://docs.bokeh.org/en/3.0.3/docs/reference/models/ranges.html#bokeh.models.DataRange1d
    p.y_range.start = ...
    p.y_range.end = ...
    
    ## 2.3: Use CDSView to create two filters on the stock data
    
    # 'inc' keeps the data where the close price is higher than the open price
    # 'dec' does the opposite of 'inc' 
    # https://docs.bokeh.org/en/latest/docs/user_guide/basic/data.html#filtering-data
    inc = ...
    dec = ...
    
    inc_view = ...
    dec_view = ...

    ## 2.4: Draw the glyphs in the candlesticks

    # A candlestick consists of a segment and a vbar
    
    # Set the width of the vbar
    # Note that the unit of datetime axis is milliseconds
    # while the interval of the stock data is week
    w = ...
    
    # Draw the segement and the vbar
    # inc vbars are green, dec vbars are red
    stock_segment = p.segment(
        ...
    )
    
    stock_inc = p.vbar(
        ...
    )

    stock_dec = p.vbar(
        ...
    )
    
    ## 2.5: Add volume bars in the candlestick chart
    
    # Note that volume data is different from stock price data in unit and scale
    # You'll create a twin y axis for volume on the right side of the chart
    # https://docs.bokeh.org/en/3.0.2/docs/user_guide/basic/axes.html#twin-axes
    # https://docs.bokeh.org/en/latest/docs/reference/models/axes.html#bokeh.models.LinearAxis

    y_volume = ...
    p.extra_y_ranges['volume'] = ...
    
    y_volume_axis = ...
    
    p.add_layout(y_volume_axis, 'right')
    
    stock_volume = p.vbar(
        ...
    )
    
    ## 2.6: Add a hover tool for the candlesticks

    # https://stackoverflow.com/questions/61175554/how-to-get-bokeh-hovertool-working-for-candlesticks-chart
    hover_stock = HoverTool()
    hover_stock.tooltips=[
        ...
    ]
    
    hover_stock.formatters={
      ...
    }
    
    # This hover tool only shows tooltips on the vbars in the candlesticks, thus you need to specify the renderers
    hover_stock.renderers = [
        ...
    ]
    p.add_tools(hover_stock)
    
    p.output_backend = 'svg'
    
    return p

# Task 3: Add Metrics Plot to the Candlestick Chart

def add_metrics_plot(main_plot):
    
    p = main_plot
    symbol = p.title.text

    # See how bokeh deals with data source containing nan values
    # https://docs.bokeh.org/en/latest/docs/user_guide/basic/lines.html#missing-points
    # Note that this might not work if the source is created from ColumnDataSource
    source = ...
    
    ## 3.1: Set the y axes for the metrics

    # 'PE Ration' and 'EPS Growth' also have different units from the stock price
    # You'll set a y axis for each metric
    # and make the extra y axes invisible
    y_pe = source['PE Ratio']
    y_eps = source['EPS Growth']
    
    p.extra_y_ranges['pe'] = Range1d(...)

    p.extra_y_ranges['eps'] = Range1d(...)
    
    y_pe_axis = LinearAxis(...)

    y_eps_axis = LinearAxis(...)
    
    ## 3.2 Use scatter and line glyphs to plot the metrics
    pe_l = p.line(
        ...
    )
    
    pe_c = p.circle(
        ...
    )
    
    eps_l = p.line(
        ...
    )
    
    eps_c = p.circle(
        ...
    )
    
    ## 3.3: Make the legend of metrics interactive
    
    # Click on a legend to mute the corresponding glyph(s)
    # https://docs.bokeh.org/en/latest/docs/user_guide/interaction/legends.html#hiding-glyphs
    p.legend.click_policy= ...

    # Set the attributes of the legend to adjust its postion, color and size
    # https://docs.bokeh.org/en/latest/docs/reference/models/annotations.html#bokeh.models.Legend
    p.legend.location = 'top_left'
    p.legend.orientation = 'horizontal'
    p.legend.background_fill_alpha = 0
    p.legend.border_line_alpha = 0
    p.legend.label_text_font_size = '10px'
    p.legend.glyph_width = 16
    
    ## 3.4: Add a hovertool for the scatter glyphs

    metrics_hover = HoverTool()
    metrics_hover.tooltips=[
        ...
    ]
    metrics_hover.formatters={
      ...
    }
    metrics_hover.mode='mouse' 
    metrics_hover.renderers = ...                
    p.add_tools(metrics_hover) 
    
    return p

# (optional) Task 4: Add a Range Selection Plot

# Add a plot with a range tool to select and zoom 
# a region in the candlestick chart
# https://docs.bokeh.org/en/latest/docs/user_guide/topics/timeseries.html#range-tool
def add_select_range(main_plot):
    
    p = main_plot
    
    select = figure(
        ...
    )
    
    range_tool = ...
    range_tool.overlay.fill_color = 'navy'
    range_tool.overlay.fill_alpha = 0.2

    select.line(
        ...
    )
    
    select.ygrid.grid_line_color = None
    select.add_tools(range_tool)
    select.toolbar.active_multi = range_tool
    select.output_backend = 'svg'

    # Put the candlestick chart and the range plot in a column 
    # with responsive sizing in width
    # https://docs.bokeh.org/en/3.0.3/docs/user_guide/basic/layouts.html#sizing-modes
    _p = ...

    return _p

# Example output
p = create_candlestick_chart('AAPL')
p = add_metrics_plot(p)
p = add_select_range(p)

output_file('dvc_ex2.html')
save(p)
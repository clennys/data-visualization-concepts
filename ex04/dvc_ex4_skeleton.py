# ====================================================================
# Goal: Build an interactive map with animation

# Task 1: Data Processing
# Task 2: Visualization
# Task 3: Interaction 
# Task 4: Animation
# ====================================================================

# This map shows the geographic distribution of tech companies in the US.
# Each circle upon one city in the map represents the total market cap 
# and the number of employees of the companies in that city,
# which are encoded in the color and size respectively.

# The user can tap on a circle in the map to show in the subplot 
# the market cap and number of employees of each company in that city.

# The user can use the slider to change the lower bound of the market cap
# to filter out the companies with a market cap smaller than this value.

# The user can click the play button to see the animation of the changes 
# in the market cap and the number of employees over the years.

# Setting up:
# This script runs with Bokeh version 3.1.0

import pandas as pd
import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Div, Range1d, WMTSTileSource
from bokeh.plotting import figure
from bokeh.transform import log_cmap
from bokeh.palettes import Turbo256
from bokeh.models import (ColumnDataSource, NumeralTickFormatter, 
                          HoverTool, Label, Button, Slider, Text)

# ====================================================================
# Task 1: Data Processing
# ====================================================================

# Read the raw data and inspect the rows and columns
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vStUglUExt-kL-fVYcit-h4-V1Vg3HUkvDEV6KwZGw_6r46duWKYx9ZGI5Bctkrv05DF0nEWYqR14Qb/pub?gid=860901304&single=true&output=csv'
us_company_map = pd.read_csv(url)

# The part of plotting the map is not required in the tasks.
# To learn more about it, you are recommended to go through the contents in
# Bokeh Tutorial 09. Geographic Plots
# https://nbviewer.org/github/bokeh/bokeh-notebooks/blob/master/tutorial/09%20-%20Geographic%20Plots.ipynb

# The longitude and latitude (degrees) of the cities
# are in the column 'lng' and 'lat' respectively.
# In order to plot the cities on the map,
# You need to convert them to web Mercator coordinates (meters)
# and store them in the columns 'x' and 'y' respectively.
# A brief explanation of web Mercator projection:
# https://stackoverflow.com/questions/14329691/convert-latitude-longitude-point-to-a-pixels-x-y-on-mercator-projection
k = 6378137 # Earth radius in meters
us_company_map["x"] = us_company_map.lng * (k * np.pi/180.0)
us_company_map["y"] = np.log(np.tan((90 + us_company_map.lat) * np.pi/360.0)) * k

# Specify the WMTS (Web Map Tile Service) Tile Source to create the map
# reference:
# https://docs.bokeh.org/en/latest/docs/user_guide/topics/geo.html#ug-topics-geo-tile-provider-maps
# https://docs.bokeh.org/en/latest/docs/examples/plotting/airports_map.html
tile_options = {
    'url': 'http://tile.stamen.com/terrain/{Z}/{X}/{Y}.png',
    'attribution': """
        Map tiles by <a href="http://stamen.com">Stamen Design</a>, under
        <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>.
        Data by <a href="http://openstreetmap.org">OpenStreetMap</a>,
        under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.
    """
}
tile_source = WMTSTileSource(**tile_options)

# Set the initial values of the `year``, 
# the `city`` to show in the subplot,
# and the lower bound of market cap in the slide.
year = 2022
city = 'San Jose'
market_cap_lower = 0

## 1.1 Define a function create the data frames for the main plot and subplot.

# According to the specified `year`, `city`, and `market_cap_lower`,
# this function will take the necessary parts from the original data us_company_map, 
# do processing and calculation, and return the data frames for the plots.
# When these values change, this function will be called to create new data frames. 

def create_df(year, city, market_cap_lower, main=True):
    
    # Take 'Symbol', 'City', 'x', 'y', and Market Cap, Employees in this `year`.
    # Rename the columns of Market Cap and Employees in this `year` 
    # to 'Market Cap' and 'Employees'.
    ...  

    # Find the companies with Market Cap below `market_cap_lower` (note the nan values)
    # and replace their 'Symbol', 'Market Cap', and 'Employees' with `np.nan`.
    ...
    
    # For the main plot, group the companies by 'City' and aggregate the data.
    # 'Market Cap' and 'Employees' are summed up,
    # 'x' and 'y' are averaged, and 'Symbol' is counted.
    # reference:
    # https://stackoverflow.com/questions/70879727/apply-same-aggregation-on-multiple-columns-when-using-groupby-python    
    if main:
        ...    
    # For the subplot, find the companies in the selected `city`
    else:
       ...
    # Calculate 'circle_size' which is proportional to the log of 'Employees'
    ...
    
    return ...

# Create the initial data frames for the main and subplot
main_df = create_df(year, city, market_cap_lower)
sub_df = create_df(year, city, market_cap_lower, main=False)

# ====================================================================
# Task 2: Visualization
# ====================================================================

## 2.1 Define a function to draw the main plot

# The main plot shows a circle on the location of each city 
# representing the companies in that city.
# The size and color of the circle correspond to 
# the total number of employees and the total market cap (both in the log scale)
# of the companies in that city respectively.

def plot_city(main_df, tile_source):

    main_source = ColumnDataSource(main_df)
    
    # Set the x and y ranges of the map initially shown in the main plot
    # to be slightly larger (e.g. 200 km) than the (min, max) of 'x' and 'y'.
    x_range = ...
    y_range = ...    
    p = figure(
        width=800, 
        height=600,
        tools='tap,wheel_zoom,pan,reset',
        toolbar_location="below", 
        x_range=x_range, 
        y_range=y_range,
        title='US Tech Companies Distribution by City'
    )

    # Add the map tile layer in the background
    # Hide the axis and grid lines
    p.add_tile(tile_source)
    p.axis.visible = False
    p.grid.grid_line_color = None
    # Create a color mapper for the circle fill color
    # which maps the 'Market Cap' (log scale) to a color palette
    color_mapper = log_cmap( ... )
    c = p.circle(
        x='x', 
        y='y', 
        # Use the calculated circle size
        size=..., 
        fill_color=...,
        alpha=0.5,
        nonselection_fill_alpha=0.2, 
        line_color="white", 
        line_width=1, 
        source=main_source,
    )
    # Construct a color bar for the circle glyph
    color_bar = ...
    p.add_layout(color_bar, 'left')
    
    # Add a hover tool to the circle glyph to show the name of the city 
    # and the number of companies in that city.
    # Note that each of these companies has a market cap in the current `year` 
    # larger than the lower bound set by the slider.
    hover_city = HoverTool()
    hover_city.tooltips= ...
    hover_city.renderers = ...        
    p.add_tools(hover_city)

    return p

main_plot = plot_city(main_df, tile_source)

# Add the label on the left bottom corner of the main plot
# that shows the current `year`.
# It will be updated when the `year` changes.
label = Label(
    ...
)

main_plot.add_layout(label)

## 2.2 Define a function to draw the subplot

# The subplot shows the companies in the city 
# selected by the tap tool in the main plot.
# Each circle represents one company.
# The size and color of the circle correspond to 
# the number of employees and the market cap (both in the log scale)
# of the company respectively.

# Find the (min, max) of 'Market Cap' and 'Employees' in us_company_map
markt_max, markt_min =  ...
emp_max, emp_min = ...

def plot_company(sub_df):
    
    sub_source = ColumnDataSource(sub_df)
    
    # Set the x and y ranges to be slightly larger than
    # the (min, max) of 'Employees' and 'Market Cap'
    # that you've found in the previous step,
    # so that the x and y ranges of the subplot remain the same 
    # when `city` or `year` changes.
    x_range = ...
    y_range = ...
    p = figure(
        width=450,
        height=400, 
        min_border=20,
        min_border_top=45,
        x_range=x_range,
        y_range=y_range,
        x_axis_type="log",
        y_axis_type="log",
        y_axis_location="right", 
        # Note that the title of the subplot will be updated 
        # when `city` or `year` changes.
        title= ...,
        tools='pan, wheel_zoom, reset', 
        toolbar_location='right'
    )
    p.xaxis.axis_label = 'Number of Employees'
    p.yaxis.axis_label = 'Market Cap in Billion USD'
    p.xaxis.formatter = NumeralTickFormatter(format='0,0 a')
    p.yaxis.formatter = NumeralTickFormatter(format='0,0.00 a')
    p.background_fill_color = "#fafafa"

    color_mapper = ...
    c = p.circle(
        x= ...,
        y= ...,
        size= ..., 
        alpha=0.5,
        fill_color=color_mapper, 
        line_color="white", 
        line_width=1.5, 
        source=sub_source,
    )
    # Add a hover tool to the circle glyph to show the symbol of the company, 
    # the market cap, and the number of employees. 
    hover_company = HoverTool()
    hover_company.tooltips=[
           ...
    ]
    hover_company.renderers = ...        
    p.add_tools(hover_company)

    # (Optional) Add the Text glyph to show the symbol on the circle 
    # reference:   
    # https://docs.bokeh.org/en/3.1.0/docs/reference/models/glyphs/text.html
    t = Text(
       ...
    )
    p.add_glyph(sub_source, t)

    return p

subplot = plot_company(sub_df)

# ====================================================================
# Task 3: Interaction
# ====================================================================

## 3.1 Define a callback function for the tap tool in the main plot

# When a city is selected on the main plot by the tap tool, 
# the subplot will be updated to show the companies in that city,
# and the title of the subplot will change accordingly.
# reference:
# https://stackoverflow.com/questions/55538391/how-to-use-tap-in-bokeh-to-effect-changes-in-a-different-plot-or-table
# https://stackoverflow.com/questions/61600714/bokeh-server-change-color-of-glyph-on-select-with-tap-tool

def tap_update(attr, old, new):
    if new:
        global city
        # get the selected city name from the main plot
        city = ...
        # update the data source of the glyphs in the subplot
        sub_df = ...
        ...
        # update the title of the subplot
        ...

main_plot.renderers[1].data_source.selected.on_change(..., tap_update)

## 3.2 Add a slider and define a callback function for it to filter companies by the market cap

# When the user changes the value of the lower bound of the market cap,
# the companies will be filtered by the new value,
# so that only those with a market cap larger than 
# the lower bound are included.
# The data source of the glyphs in the main plot 
# and the subplot will be updated accordingly.
# reference:
# https://github.com/bokeh/bokeh/blob/branch-3.1/examples/server/app/sliders.py

slider = Slider(
    ...
)

def slider_update(attr, old, new):
    global market_cap_lower
    ...

slider.on_change(..., slider_update)

# ====================================================================
# Task 4: Animation
# ====================================================================

# Add a play button to show the animation of changes in the market cap
# and the number of employees over the years in the main plot and the subplot.
# reference:
# https://github.com/bokeh/bokeh/tree/branch-3.1/examples/server/app/gapminder

btn = Button(
    ...
)

## 4.1 Define a function to update the elements that change along with the year.

# The `year` will be incremented by 1 till the last year (2022), 
# then go back to the first year (2019).
# The year in the main plot and the title of the subplot will be updated accordingly.
# The data source of the glyphs in the main plot and subplot will be updated accordingly.

def update_year():
    global year
    ...

## 4.2 Define a function to wrap the update function in a periodic callback.

# This callback will be associated with the Bokeh document and triggered by button clicks.
# When the user clicks on '► Play', the button label will change to '❚❚ Pause'.
# The callback will be invoked to execute `update_year` periodically at an interval of 1 second.
# When the user clicks on '❚❚ Pause', the button label will change back to '► Play'.
# The callback will be removed and the execution of `update_year` will stop.
# reference:
# https://docs.bokeh.org/en/latest/docs/reference/server/callbacks.html#bokeh-server-callbacks
# https://docs.bokeh.org/en/3.1.0/docs/reference/document.html#bokeh.document.Document.add_periodic_callback       

callback = None
def play():
    global callback
    ...

btn.on_click(play)

# (Optional) Add a text div to explain your app to the user.
div = ...

layout = row([main_plot, column(subplot, slider, div, btn)])
curdoc().add_root(layout)
curdoc().title = 'US Tech Companies Distribution by City'

# ====================================================================
# Mission Complete! ✅
# ====================================================================
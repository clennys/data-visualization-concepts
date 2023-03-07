# Activate the bokeh environment
# You may refer to:
# bokeh tutorial 00 - Introduction and Setup - Getting set up

# Import dependencies

import pandas as pd
from bokeh.plotting import figure 
from bokeh.io import output_file, save
from bokeh.models import ColumnDataSource, HoverTool, FactorRange, NumeralTickFormatter
from bokeh.layouts import gridplot
from bokeh.transform import factor_cmap
from bokeh.models.annotations import Label
from bokeh.palettes import Blues3

# Task 1: Prepare the Data

## 1.1: Use pandas to read a csv file into a dataframe from a link

# You may refer to:
# https://pythoninoffice.com/how-to-read-google-sheet-into-pandas/

url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQdNgN-88U31tk1yQytaJdmoLrxuFn1LnbwTubwCd8se2aHh8656xLLHzxHSoiaXMUu8rIcu6gMj5Oq/pub?gid=1242961990&single=true&output=csv'
MAGMA_financials = pd.read_csv( ... )

## 1.2: Inspect the columns in the dataframe

# 'Symbol': 
# The stock ticker symbols of five companies
# META, AAPL, GOOGL, MSFT, AMZN 

# 'Quarter Ended': 
# The time when the companies filed their quarterly financial statements to SEC
# from 2019Q1 to 2022Q4

# The other columns, 'Revenue', 'Gross Profit', etc. 
# are several items in the financial statements

# Your task is to select a subset of the financial items of a company
# and visualize them in a grouped bar chart

# Select a subset of the financial items,
# e.g. ['Net Income', 'Operating Expenses', 'Selling, General & Admin']

subset = [ ... ]

## 1.3: Create a nested categorical coordinate

# To see the trend, you'll use 'Quarter Ended' in the x axis
# Each item has 16 quarters' data, and each quarter has a subset of items
# To make the x axis clear and readable, 
# you'll create a nested (hierarchical) categorical coordinate as x
# Namely, it will group the bars in nested levels of (year, quarter, item)
# e.g. x = [ ('2019', 'Q1', 'item 1'),  ('2019', 'Q1', 'item 2'), ...]

# You may refer to:
# bokeh tutorial 07 - Bar and Categorical Data Plots - Grouped Bar Charts

years = ['2019', '2020', '2021', '2022']
quarters = ['Q1', 'Q2', 'Q3', 'Q4']
x = [ ... ]

## 1.4: Use ColumnDataSource to generate data sources

# For reusability, you'll define a function to create the data source
# You may refer to:
# bokeh tutorial 03 - Data Sources and Transformations - Creating with Python Dicts
# This function takes a company symbol as an argument
# and returns the corresponding data source

def create_source(symbol):
    
    # Select the company's data from the dataframe
    # You may refer to:
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html
    
    data = MAGMA_financials[MAGMA_financials.Symbol == symbol][subset]
    
    # Flatten the data to a 1d list as y
    # corresponding to the nested categorical coordinate of x axis
    # You may refer to:
    # https://www.datasciencelearner.com/flatten-dataframe-in-pandas-methods/
    
    y = list( ... )

    # To make the legends later in the bar chart, 
    # you'll give each bar its item name as a label,
    # and put these labels into a legend group
    # with the column name 'label' in the data source
    # You may refer to:
    # https://docs.bokeh.org/en/latest/docs/user_guide/basic/annotations.html#automatic-grouping-python-side
    
    x_label = ...
    
    return ColumnDataSource(data= ... )

# Create a source for each company
# and put them in a dictionary in the format
# sources = { symbol : source, ... }

symbols = MAGMA_financials.Symbol.unique()
sources = {symbol : create_source(symbol) for symbol in symbols}


# Task 2: Draw the Bar Chart

## 2.1: Configure the settings of the figure 

# Set the width and hight of the figure
# You'll add a hover tool later, for now set the tools to empty

options = dict(width = 700, height = 200, tools='')

# For reusability, you'll define a function for drawing the bar chart
# This function takes a company symbol as an argument
# and returns the corresponding barchart

def draw_bar_chart(symbol):
    
    p = figure(

        # Use FactorRange to create the x_range
        # You may refer to:
        # bokeh tutorial 07 - Bar and Categorical Data Plots - Grouped Bar Charts

        x_range = ... , 
        title = symbol, 
        **options
    )

    # Hide the x grid line
    p.xgrid.grid_line_color = ...

    # Pad the x range
    p.x_range.range_padding = ...

    # You'll use the legend group to show the item names of the bars
    # So hide the default labels and ticks on x axis
    # You may refer to:
    # bokeh tutorial 02 - Styling and Theming - Axes

    # Hide the labels on x axis
    p.xaxis.major_label_text_font_size = ...

    # Hide the x major tick line
    p.xaxis.major_tick_line_color = ...

    # Set the y axis label to 'millions USD'
    p.yaxis.axis_label = ...

    # Use NumeralTickFormatter to a comma as the thousand separator
    p.yaxis.formatter = NumeralTickFormatter( ... )

## 2.2: Configure the bar glyphs

    p.vbar(
            # Draw the bars from the source corresponding to the company symbol 
            x = ... , top = ... , width = ... , 
            source = ... ,

            # Use the column 'label' in the data source as the legend group
            legend_group = ... ,
            line_color = ... ,
            
            # Use factor_cmap to assign colors to bars accroding to their item names
            # You may refer to:
            # bokeh tutorial 07 - Bar and Categorical Data Plots - Grouped Bar Charts

            fill_color=factor_cmap(
                ... , palette = ... , 
                factors = ... , start = ... , end = ...
            )
          )

## 2.3: Add a hover tool

    # When you hover over a bar, the tooltip will show (year, quarter, item: value)
    # Note that (year, quarter, item) is the nested categorical coordinate in x
    # and data is the value in y
    # The (label, value) tuple in the tooltip can be ('', 'value1 : value2') 
    # You may refer to:
    # https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#hovertool
    # You can also format tooltips, e.g. add a comma as thousand separator to the value:
    # https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#formatting-tooltip-fields

    p.add_tools(HoverTool(tooltips=[
        ( ... ),
    ]))

## 2.4: Add a legend

    # Set the legend label and glyph sizes
    # You may refer to:
    # https://stackoverflow.com/questions/29130098/how-do-you-change-size-of-labels-in-the-bokeh-legend-in-python
    
    p.legend.label_text_font_size = ...
    p.legend.label_height = ...
    p.legend.glyph_height = ...
    p.legend.glyph_width = ...

    # Set the legend orientation and location
    p.legend.orientation = ...
    p.legend.location = ...
    
    # Set the output_backend to 'svg' to preserve the resolution when zooming in
    p.output_backend = "svg"
    
    return p

## 2.5(optional): Add a text label

# For the companies that have announced layoffs in the past few months
# (META, AMZN, GOOGL, MSFT),
# you'll add a text label on the bar chart to show '(time) layoffs (number)'
# You may refer to:
# bokeh tutorial 04 - Adding Annotations - Label
# https://docs.bokeh.org/en/latest/docs/user_guide/basic/annotations.html#labels

# For reusability, you'll define a function for making the text labels

def make_label(time, number):
    
    label = Label(
        
        # Set the postion of the label (x, y) using screen units
        x = ... , 
        y = ... , 
        x_units = ... ,
        y_units = ... ,
        
        # Set the text content, font size, color, align, background
        text = f'{time}\nlayoffs\n{number}',
        text_font_size = ... ,
        text_font_style = ... , 
        text_color = ... ,
        text_align = ... ,
        background_fill_color = ... , 
        background_fill_alpha = ...
    )
    
    return label

# Make a dictionary of the text labels with the provided time and number information

labels = {
    'AMZN':  make_label('Jan 2023', '18,000'),
    'META': make_label('Nov 2022', '11,000'),
    'GOOGL': make_label('Jan 2023', '12,000'),
    'MSFT': make_label('Jan 2023', '10,000'),
}

# Draw a bar chart with label

p_META = draw_bar_chart('META')
p_META.add_layout( ... )


## 2.6(optional): Put two bar charts in a gridplot vertically for comparison

# You may refer to:
# bokeh tutorial 05 - Presentation Layouts - Grid plots

p_AAPL = draw_bar_chart('AAPL')
p = gridplot([
     ...
], toolbar_location = None)

## 2.7: Save the bar chart(s) to a html file with the filename 'dvc_ex1.html'

# You may refer to:
# bokeh tutorial 10 - Exporting and Embedding - Saving to an HTML File

output_file('dvc_ex1.html')
save(p)

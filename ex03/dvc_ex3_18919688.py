# ====================================================================
# Goal: Build an interactive visualization app with Bokeh server

# Task 1: Dimension Reduction
# Task 2: Visualization
# Task 3: Interaction
# ====================================================================

# Please refer to Bokeh Tutorial 11. Running Bokeh Applications - Bokeh Apps with bokeh serve
# https://hub.gke2.mybinder.org/user/bokeh-bokeh-notebooks-zbqmazt5/doc/tree/tutorial/11%20-%20Running%20Bokeh%20Applications.ipynb

# How to use Bokeh server to build application:
# https://docs.bokeh.org/en/latest/docs/user_guide/server/app.html

# To see the interactive visualization app,
# pleae run this script in the terminal with the command:
#   bokeh serve --show YOURFILENAME.py
# It will be opened in the browser: http://localhost:5006/YOURFILENAME.
# To stop the app, press ctrl+c in the terminal

# Setting up:
# This script runs with bokeh version 3.1.0
# For the principal component analysis and clustering tasks,
# please install sciket-learn:
# https://scikit-learn.org/stable/install.html

# import packages for processing data
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_object_dtype

# import packages for principal component analysis and clustering
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn import cluster
from sklearn.impute import SimpleImputer

# import packages for visualization
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, HoverTool, LassoSelectTool, Select
from bokeh.palettes import TolRainbow, Turbo256
from bokeh.transform import factor_cmap, linear_cmap, log_cmap

# ====================================================================
# Task 1: Dimension Reduction
# ====================================================================

# Read the raw data and inspect the rows and columns.
# There are 5 categorical columns (Country, Industry, Company, Symbol, Recommendation)
# and 102 numerical columns (i.e. features).

pca_data_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFGt2FAUh_Fb7XAtYasA95ut8X_4a6sqizwcF-QFHdxULsPCf0kXhqn3wJdxNE2Ogf-f1qwyeOIySw/pub?gid=1323235&single=true&output=csv"
pca_data = pd.read_csv(pca_data_url)

## 1.1 Principal component analysis (PCA)

# You'll project the 102 numeric features to 2 dimensions using PCA.
# Reference:
# https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html


def pca(df):

    # select the numeric features
    X = df.iloc[:, 5:]  # 5th to last cols
    # use MinMaxScaler to scale the features
    X_scaled = MinMaxScaler().fit_transform(X)
    # use SimpleImputer to fill in the missing values with the mean value
    # imp = SimpleImputer(missing_values=np.nan, strategy="mean")
    imp = SimpleImputer(strategy="mean")
    X_imp = imp.fit_transform(X_scaled)
    # perform PCA to project the features into 2 components
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_imp)
    # append the 2 principal components to the dataframe
    df["PCA 1"] = X_pca[:, 0]
    df["PCA 2"] = X_pca[:, 1]

    return df


# 1.2 Clustering

# You'll divide the data points into 2 (or more) clusters
# based on the principal components and assign a cluster label to each point.
# Reference:
# https://scikit-learn.org/stable/modules/clustering.html#clustering
# https://github.com/bokeh/bokeh/tree/branch-3.1/examples/server/app/clustering


def clustering(df, n_clusters=2):

    # select the principal components
    X_pca = df.iloc[:, -2:]
    # sets the random seed to 0 so that the result is reproducible
    np.random.seed(0)
    # use MiniBatchKMeans to perform the clustering
    model = cluster.MiniBatchKMeans(n_clusters=n_clusters, n_init=2)
    model.fit(X_pca)
    # append the cluster labels to the dataframe
    y_pred = model.labels_.astype(str)
    df["Cluster"] = y_pred

    return df


# ====================================================================
# Task 2: Visualization
# ====================================================================

# The visualization includes 3 parts:
# 1) A main plot that shows the data points by the 2 principal components.
#    You'll assign a color map on the points according a selected feature.
#    If the feature is numeric, the color map will be continuous, accompanied by a color bar.
#    If the feature is categorical, the color map will be discrete, accompanied a legend.
# 2) A subplot that shows the statistic of a selected feature.
#    If the feature is numeric, the subplot will be a histogram.
#    If the feature is categorical, the subplot will be a bar chart.
# 3) Two selection widgets,
#    one to select the feature to apply the color map in the main plot,
#    one to select the feature to show in the subplot.

## 2.1 Define a function to create a color map for the selected feature.


def create_cmap(df, col):
    # create a discete color mapper (factor_cmap) for categorical features
    if is_object_dtype(df[col]):
        l = np.unique(df[col].astype(str))
        # use a palette from bokeh:
        # https://docs.bokeh.org/en/latest/docs/reference/palettes.html#d3-palettes
        # if the feature is binary, you'll need to explicitly make a list of colors
        nr_colors = len(l)
        palette = TolRainbow[nr_colors] if nr_colors > 2 else ["yellow", "purple"]
        mapper = factor_cmap(col, palette=palette, factors=l)
        # (Optional) make a dictionary of category:color pairs
        # it will be used to synchronize the colors in the main plot and the (optional) bar chart
        cat_palette = {l[i]: palette[i] for i in range(len(l))}
    # create a continuous color mapper (linear_cmap or log_cmap) for numeric features
    # https://docs.bokeh.org/en/3.1.0/docs/examples/basic/data/color_mappers.html
    elif is_numeric_dtype(df[col]):
        palette = Turbo256
        low, high = min(df[col]), max(df[col])
        if min(df[col]) >= 0:
            mapper = log_cmap(col, palette=palette, low=low, high=high)
        else:
            mapper = linear_cmap(col, palette=palette, low=low, high=high)
        cat_palette = None

    return mapper, cat_palette


## 2.2 Define a function to plot the principal components.

# You'll pass in a ColumnDataSource as the source
# The dataframe is not used directly as the source
# because you'll use the lasso selection tool
# which works with ColumnDataSource
# ft_selected is the selected feature to apply the color map


def plot_pca(source, df, ft_selected):

    c = ft_selected
    p = figure(
        title=f"PCA with Color Map on {c}",
        tools="hover, pan, wheel_zoom, lasso_select, reset",
        tooltips=[("", "@Symbol")],
        toolbar_location="below",
        width=500,
        height=450,
    )
    # use the function in 2.1 to create a color map for the selected feature
    mapper, _ = create_cmap(df, c)
    r = p.circle(
        # use the 2 principal components as x and y
        x="PCA 1",
        y="PCA 2",
        size=8,
        # apply the color map on the glyphs
        fill_color=mapper,
        alpha=0.4,
        line_color=None,
        # the source will have a column named 'label'
        # which is a copy of the selected feature
        # if the selected feature is categorical
        # this 'label' column will be used to generate the legend
        legend_field="label",
        source=source,
    )
    # p.sizing_mode = 'stretch_both'
    p.background_fill_color = "#fafafa"
    p.xaxis.axis_label = "PCA component 1"
    p.yaxis.axis_label = "PCA component 2"

    # for a numeric feature, create a color bar
    # https://docs.bokeh.org/en/latest/docs/user_guide/basic/annotations.html#color-bars
    if is_numeric_dtype(df[c]):
        color_bar = r.construct_color_bar(padding=5)
        p.add_layout(color_bar, "left")
        # remove automatically generated the legend
        # https://discourse.bokeh.org/t/how-to-remove-legend-from-the-plot/5208/3
        p.legend.items = []
    # for a categorical feature, put the legend to the left of the plot
    elif is_object_dtype(df[c]):
        p.add_layout(p.legend[0], "left")
    # set the 'continuous' property of the lasso select tool to False
    # so that the computation to happen after (not during) the selection
    # https://docs.bokeh.org/en/3.1.0/docs/reference/models/tools.html#bokeh.models.LassoSelectTool
    p.select(LassoSelectTool).continuous = False
    p.output_backend = "svg"

    return p


## 2.3 Define a function to draw the histogram for a numeric feature.

# The histogram has two sets of bins:
# set 1 shows the histogram of all the points in the PCA plot
# set 2 shows the histogram of the points selected by the lasso selection tool in the PCA plot
# Example:
# https://docs.bokeh.org/en/latest/docs/examples/topics/stats/histogram.html#index-0
# https://github.com/bokeh/bokeh/blob/branch-3.1/examples/server/app/selection_histogram.py

def draw_hist(df, col, points_selected):
    # get the corresponding rows in the dataframe for the selected points
    s = df.iloc[points_selected]
    # compute the tops and edges of the bins in the histogram
    # for all the points and the selected points respectively
    hist_values, bin_edges = np.histogram(df[col].dropna().reset_index(drop=True), bins=len(df[col]))
    hist_value_selected, _ = np.histogram(s[col].dropna().reset_index(drop=True), bins=bin_edges)
    # create a data source for both sets of bins
    source = ColumnDataSource(
        data=dict(
            range_start=bin_edges[:-1],
            range_end=bin_edges[1:],
            hist_v=hist_values,
            hist_vs=hist_value_selected,
        )
    )

    ph = figure(
        width=400,
        height=300,
        min_border=20,
        y_range=(0, 1.1 * hist_values.max()),
        y_axis_location="right",
        title=f"Histogram of {col}",
        tools="pan, wheel_zoom, reset",
        toolbar_location="below",
    )

    ph.xaxis.axis_label = f"{col}"
    ph.yaxis.axis_label = "Counts"
    ph.xgrid.grid_line_color = None
    ph.background_fill_color = "#fafafa"
    # draw the bins of all points
    h_a = ph.quad(
        bottom=0,
        left="range_start",
        right="range_end",
        top="hist_v",
        source=source,
        legend_label="all",
        color="silver",
        line_color="silver",
    )
    # draw the bins of selected points
    h_s = ph.quad(
        bottom=0,
        left="range_start",
        right="range_end",
        top="hist_vs",
        source=source,
        legend_label="selected",
        color="purple",
        line_color=None,
        alpha=0.5,
    )
    ph.legend.orientation = "horizontal"
    ph.legend.location = "top_right"
    # add a hover tool that shows the values of
    # the range (left and right edges) of a bin
    # the counts of all points in the bin
    # the counts of selected points in the bin
    hover = HoverTool()
    hover.tooltips = [
        ("range", "[@range_start, @range_end]"),
        ("all", "@hist_v"),
        ("selected", "@hist_vs"),
    ]
    # to avoid overlap, apply the hover tool only on the bins of all points
    hover.renderers = [h_a]
    ph.add_tools(hover)

    return ph


## 2.4 (Optional) Define a function to draw a bar chart for a categorical feature.

# The bar chart has two sets of bars:
# set 1 shows the bars of all the points in the PCA plot
# set 2 shows the bars of the points selected by the lasso selection tool in the PCA plot


def draw_bar_chart(df, col, points_selected):
    # get the corresponding rows in the dataframe for the selected points
    s = ...
    # count the number in the categories
    # for all the points and the selected points respectively
    dis = df[col].value_counts()
    dis_s = s.value_counts()
    cat = dis.index.values
    count = dis.values
    # note that if the selected points do not have a certain category
    # the corresponding count should be zero
    count_s = []
    for c in cat:
        ...
    # use the color palette you created before in the create_cmap function
    # synchronize the color map of the bars with the pca plot
    # i.e. each category should have the same color in the pca plot and the bar chart
    _, cat_palette = create_cmap(df, col)
    cat_color = ...
    # create a data source for both sets of bars
    source = ColumnDataSource(data=dict(...))

    pb = figure(
        x_range=cat,
        y_range=(0, count.max() * 1.1),
        y_axis_location="right",
        width=400,
        height=300,
        min_border=20,
        title=f"Distribution of {col}",
        tools="pan, wheel_zoom, reset",
        toolbar_location="below",
    )

    pb.background_fill_color = "#fafafa"
    pb.xaxis.axis_label = f"{col}"
    pb.yaxis.axis_label = "Counts"
    # draw the bars of all points
    bar_all = pb.vbar(
        x=...,
        top=...,
        width=0.6,
        color="white",
        line_color="silver",
        legend_label="all",
        source=source,
    )
    # draw the bars of selected points
    bar_selected = pb.vbar(
        x=...,
        top=...,
        width=0.6,
        color="color",
        alpha=0.4,
        legend_label="selected",
        source=source,
    )

    pb.xgrid.grid_line_color = None
    pb.xaxis.major_label_orientation = np.pi / 2
    pb.legend.orientation = "horizontal"
    pb.legend.location = "top_right"
    # add a hover tool that shows the values of
    # the category of a bar
    # the counts of all points in the bar
    # the counts of selected points in the bar
    hover = HoverTool()
    hover.tooltips = [("category", ...), ("all", ...), ("selected", ...)]
    hover.renderers = [...]
    pb.add_tools(hover)
    pb.output_backend = "svg"

    return pb


# Define a function to draw the subplot
# according to the data type of the selected feature
# and the indices of the selected points in the PCA plot


def draw_subplot(df, ft_selected, points_selected):
    cs = ft_selected
    rs = points_selected
    if is_numeric_dtype(df[cs]):
        sub_p = draw_hist(df, cs, rs)
    elif is_object_dtype(df[cs]):
        sub_p = draw_bar_chart(df, cs, rs)
    return sub_p


# Plotting

# Get the dataframe with principal components and cluster labels
df_pca = pca(pca_data)
df = clustering(df_pca, 2)
# Select a initial feature for the PCA plot
pca_ft_selected = "Market Cap"
# Select a initial feature for the subplot
sub_ft_selected = "Mean Recommendation"
# The initial indices of selected points is an empty list
points_selected = []

# Add a column named 'label' in the dataframe
# which is a copy the selected feature.
# It will be updated when you choose a different feature
# in the selection widget for the PCA plot.
df["label"] = df[pca_ft_selected]
# create the data source for the PCA plot using ColumnDataSource
p_pca_source = ColumnDataSource(data=df)

# Create the initial PCA plot and the subplot
p_pca = plot_pca(p_pca_source, df, pca_ft_selected)
p_sub = draw_subplot(df, sub_ft_selected, points_selected)

# ====================================================================
# Task 3: Interaction
# ====================================================================

# 3.1 Add two Select widgets

# To select the features for the PCA plot and the subplot respectively
# https://docs.bokeh.org/en/latest/docs/user_guide/interaction/widgets.html#select

select_col_pca = Select(
    title="Select a feature to apply a color map in the PCA plot:",
    value=pca_ft_selected,
    # You are free to choose which features to include in the options
    # as long as there is at least one categorical feature, e.g. 'Cluster'
    options=["Cluster", "Market Cap", "Industry", "Recommendation", "Investment Score"],
    width=200,
    margin=(20, 10, 10, 20),
)

select_col_sub = Select(
    title="Select a feature to show in the subplot:",
    value=sub_ft_selected,
    # You are free to choose which features to include in the options
    # it is optional to include any categorical feature
    options=["Mean Recommendation",  "Target Price", "RSI", "Enterprise To Revenue" ],
    width=200,
    margin=(10, 10, 10, 20),
)

# arrange the plots and widgets in a layout
layout = row(
    column(
        p_pca,
        width=500,
    ),
    column(
        select_col_pca,
        select_col_sub,
        p_sub,
        width=350,
    ),
)

# 3.2 Define the callback functions for the selection widgets

# Python callbacks:
# https://docs.bokeh.org/en/latest/docs/user_guide/interaction/python_callbacks.html#python-callbacks
# Example:
# https://github.com/bokeh/bokeh/tree/branch-3.0/examples/server/app/crossfilter
# https://stackoverflow.com/questions/38982276/how-to-refresh-bokeh-document

# Callback function of the Select widget for the PCA plot:
# when you select a new feature
# the 'label' column in the data source will be updated to the new feature
# a new PCA plot will be drawn to replace the previous one in the layout

# (Please note that replacing the whole plot is the simple way for updating a plot.
# The better practice is making the minimal changes to the properties of the existing plot,
# as the example in Bokeh Tutorial 11. Running Bokeh Applications - Linking Plots and Widgets
# https://hub.gke2.mybinder.org/user/bokeh-bokeh-notebooks-zbqmazt5/doc/workspaces/auto-E/tree/tutorial/11%20-%20Running%20Bokeh%20Applications.ipynb)


def update_pca_col(attrname, old, new):

    p_pca_source.data["label"] = p_pca_source.data[new]
    p_pca = plot_pca(p_pca_source, df, new)
    layout.children[0].children[0] = p_pca


# Callback function of the Select widget for the subplot:
# when you select a new feature
# a new subplot of this feature will be drawn to replace the previous one in the layout
# the new subplot will keep the previous selection of points by the lasso selection tool


def update_sub_col(attrname, old, new):

    global sub_ft_selected
    sub_ft_selected = new
    layout.children[1].children[2] = draw_subplot(df, new, points_selected)


select_col_pca.on_change("value", update_pca_col)
select_col_sub.on_change("value", update_sub_col)

## 3.3 Define the callback functions for the lasso selection tool in the PCA plot

# when you select some points with the lasso selection tool,
# a new subplot will be drawn to replace the previous one in the layout
# with the new selection of points reflected in the bins / bars of the selected points
# Example:
# https://github.com/bokeh/bokeh/blob/branch-3.1/examples/server/app/selection_histogram.py


def lasso_update(attr, old, new):

    global points_selected
    points_selected = new
    layout.children[1].children[2] = draw_subplot(df, sub_ft_selected, points_selected)


p_pca.renderers[0].data_source.selected.on_change("indices", lasso_update)

curdoc().add_root(layout)
curdoc().title = "PCA"

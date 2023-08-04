import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, Input, Output, dcc, dependencies
import dash_bootstrap_components as dbc
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np

# create date dictionary which can be used for users selecting the crop price data on certain date on map through the slider
end_date = datetime.now().date()
months = 12  # allow users choosing the past 12 months data
start_date = end_date - relativedelta(months=months)
date_range = pd.date_range(
    start_date, end_date, freq="MS"
)  # interval of date is per month
date_slider_dict = {i: str(dt.strftime("%B, %Y")) for i, dt in enumerate(date_range)}
date_slider_dict[
    months
] = "Latest data"  # create the latest data for users to browse all regions and markets data in the most recent update basis

int = 3  # create the date slider with interval to avoid messy label
date_label_dict = {
    int * i: str(dt.strftime("%B, %Y")) for i, dt in enumerate(date_range[::3])
}
date_label_dict[months] = "Latest data"

# the lists and dictionary are used for the dropdown options
main_category = [
    "Rice",
    "Fish",
    "Fruits",
    "Highland Vegetables",
    "Lowland Vegetables",
    "Livestock & Poultry Products",
    "Spices",
    "Other",
]
category_dict = {
    "Rice": [
        "National Food Authority",
        "Premium (Imported)",
        "Regular Milled (Imported)",
        "Special (Imported)",
        "Well-milled (Imported)",
        "Premium (Local)",
        "Regular Milled (Local)",
        "Special (Local)",
        "Well-milled (Local)",
    ],
    "Fish": [
        "Indian mackerel",
        "Milkfish",
        "Round Scad (Imported)",
        "Round Scad (Local)",
        "Tilapia",
    ],
    "Fruits": [
        "Philippine Lime",
        "Banana (Lakatan)",
        "Banana (Latundan)",
        "Mango (Carabao)",
        "Papaya",
    ],
    "Highland Vegetables": [
        "Cabbage",
        "Carrots",
        "Baguio Beans",
        "White Potato",
        "Napa Cabbage",
        "Chayote",
    ],
    "Lowland Vegetables": [
        "Bittergourd",
        "Squash",
        "Chinese Cabbage",
        "String Beans",
        "Eggplant",
        "Tomato",
    ],
    "Livestock & Poultry Products": [
        "Beef Brisket",
        "Beef Rump",
        "Egg",
        "Pork Ham",
        "Pork Liempo",
        "Whole Chicken",
    ],
    "Spices": [
        "Garlic (Imported)",
        "Garlic (Local)",
        "Ginger",
        "Red Onion",
        "Red Onion (Imported)",
        "White Onion",
        "White Onion (Imported)",
        "Chili",
    ],
    "Other": [
        "Cooking Oil (1L)",
        "Cooking Oil (350mL)",
        "Brown Sugar",
        "Washed Sugar",
        "Refined Sugar",
        "Coconut Cooking Oil (350mL)",
        "Coconut Cooking Oil (1L)",
    ],
}
regions = [
    "CAR - Cordillera Administrative Region",
    "Ilocos Region (Region I)",
    "Cagayan Valley (Region II)",
    "Central Luzon (Region III)",
    "CALBARZON (Region IV-A)",
    "MIMAROPA Region (Region IV-B)",
    "Bicol Region (Region V)",
    "Western Visayas (Region VI)",
    "Central Visayas (Region VII)",
    "Eastern Visayas (Region VIII)",
    "Zamboanga Peninsula (Region IX)",
    "Northern Mindanao (Region X)",
    "Davao Region (Region XI)",
    "SOCCSKSARGEN (Region XII)",
    "NCR - National Capital Region",
    "BARMM - Bangsamoro Autonomous Region in Muslim Mindanao",
    "Caraga (Region XIII)",
]

# legend layout for the crop price trend graph
legend_layout = dict(
    traceorder="normal",
    x=0.5,  # Set the x position of the legend to the center of the plot
    y=-0.3,  # Set the y position of the legend to be below the plot
    xanchor="center",  # Anchor the x position to the center of the legend
    yanchor="top",  # Anchor the y position to the top of the legend
    orientation="h",  # Set the orientation of the legend to horizontal
    font=dict(size=24),  # Set the font size of the legend text
    bgcolor="#E2E2E2",  # Set the background color of the legend
    bordercolor="gray",  # Set the border color of the legend
    borderwidth=1,  # Set the border width of the legend
)

# Load the GeoJSON file for the use of plotting map
with open("data/philippine_region_simplify.json") as f:
    geojson = json.load(f)

# read the crop price dataset
df = pd.read_csv("data/bantaypresyo.csv")
df = df.drop(["Specification"], axis=1)
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
df = df[df["Date"] > pd.to_datetime(start_date)]  # only sort data in the latest year
df = df.sort_values("Date")

# ------------------------------------------------------------------------------
# App layout
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "styles.css"],
    meta_tags=[{"name": "viewport", "width": "device-width, , initial-scale=5"}],
)

app.title = "Cultivest Price Monitoring"

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Main category"),
                        dcc.Dropdown(
                            className="custom-dropdown",
                            id="select_main_category",
                            options=[
                                {"label": item, "value": item} for item in main_category
                            ],
                            multi=False,
                            value=None,
                            clearable=False,
                            placeholder="Select main category...",
                            optionHeight=40,
                            style={"text-align": "left", "backgroundColor": "#f2f2f2"},
                        ),
                        html.Br(),
                        html.Label("Category"),
                        dcc.Dropdown(
                            id="select_category",
                            placeholder="Select category...",
                            clearable=False,
                            style={
                                "text-align": "left",
                                "backgroundColor": "#f2f2f2",
                                "margin": "auto",
                                "height": "100px",
                                "overflow-x": "visible",
                            },
                            optionHeight=100,
                        ),
                        html.Br(),
                        html.Br(),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Regions"),
                        dcc.Dropdown(
                            id="select_region",
                            multi=True,
                            placeholder="Filter regions",
                            style={"text-align": "left", "backgroundColor": "#f2f2f2"},
                            optionHeight=65,
                        ),
                    ],
                ),
            ],
            className="dropdowns",
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(
                            id="crop_price_map",
                            figure={},
                            style={
                                "height": "700px",
                                "width": "700px",
                                "margin": "auto",
                            },
                        ),
                    ],
                    className="crop-price-map",
                ),
                html.Div(
                    [
                        html.Div(
                            dcc.Slider(
                                id="date_slider",
                                min=0,
                                max=months,
                                step=1,
                                value=months,
                                marks=date_label_dict,
                            ),
                            className="col-md-11",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Textarea(
                                            id="textarea_1",
                                            readOnly=True,
                                            contentEditable=False,
                                            style={
                                                "width": "110px",
                                                "height": "30px",
                                                "fontSize": "18px",
                                            },
                                        )
                                    ],
                                ),
                            ],
                            className="text_area_date col-md-1",
                        ),
                    ],
                    className="row price-map-date-slider",
                ),
            ],
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Textarea(
                                    id="textarea_2_category",
                                    readOnly=True,
                                    contentEditable=False,
                                    style={
                                        "width": "100%",
                                        "height": "67%",
                                        "backgroundColor": "transparent",
                                        "border": "none",
                                        "borderRight": "1px dashed gray",
                                        "borderBottom": "2px dashed gray",
                                        "fontSize": "24px",
                                    },
                                ),
                                dcc.Textarea(
                                    id="textarea_2_date",
                                    readOnly=True,
                                    contentEditable=False,
                                    style={
                                        "width": "100%",
                                        "height": "33%",
                                        "backgroundColor": "transparent",
                                        "border": "none",
                                        "borderRight": "1px dashed gray",
                                        "fontSize": "24px",
                                    },
                                ),
                            ],
                            className="trend-category-date-box",
                        ),
                        html.Div(
                            [
                                dcc.Textarea(
                                    id="textarea_2_price_range",
                                    readOnly=True,
                                    contentEditable=False,
                                    style={
                                        "width": "100%",
                                        "height": "40%",
                                        "backgroundColor": "transparent",
                                        "border": "none",
                                        "margin": "auto",
                                        "verticalAlign": "middle",
                                    },
                                ),
                                dcc.Textarea(
                                    id="textarea_2_price_avg",
                                    readOnly=True,
                                    contentEditable=False,
                                    style={
                                        "width": "100%",
                                        "height": "60%",
                                        "backgroundColor": "transparent",
                                        "border": "none",
                                        "margin": "auto",
                                        "verticalAlign": "middle",
                                        "fontSize": "40px",
                                    },
                                ),
                            ],
                            className="trend-price-range-box",
                        ),
                    ],
                    className="trend-price-info-box",
                ),
                html.Div(
                    dcc.Graph(
                        id="crop_price_trend",
                        figure={},
                        responsive=True,
                        style={"height": "800px", "width": "100%"},
                    ),
                    className="crop_price_trend",
                ),
            ],
            className="six columns",
            style={"text-align": "center"},
        ),
    ],
    className="overall-layout",
)


# create a dependent category dropdown based on the main category choice
@app.callback(
    [dependencies.Output("select_category", "options")],
    [dependencies.Input("select_main_category", "value")],
)
def set_category_options(select_main_category):
    """
    Description: When the main category dropdown is clicked, return the category dropdown dictionaries

    Args:
    selected_main_category (str): Main category

    Returns:
    (str): Category dropdown options
    """
    if select_main_category is None:
        return [[]]
    else:
        options = [
            {
                "label": html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("icons/{}.jpeg".format(category)),
                            style={
                                "height": "90px",
                                "width": "90px",
                                "margin-right": "10px",
                                "object-fit": "cover",
                                "roundness": "50",
                            },
                        ),
                        category,
                    ],
                ),
                "value": category,
            }
            for category in category_dict[select_main_category]
        ]
    return [options]

# create a dependent region filter that the users can only choose regions the the are avilable
@app.callback(
    [dependencies.Output("select_region", "options")],
    [dependencies.Input("select_category", "value")],
)
def set_category_options(select_category):
    options=[]
    for region in regions:
        dff = df[df['Category'] == select_category]
        if not dff[dff['Region'] == region].empty:
            options.append({"label": region, "value": region})
    return options,


# graph responding part
@app.callback(
    [
        Output(component_id="crop_price_map", component_property="figure"),
        Output(component_id="crop_price_trend", component_property="figure"),
        Output("textarea_1", "value"),
        Output(component_id="textarea_2_category", component_property="value"),
        Output("textarea_2_date", "value"),
        Output("textarea_2_price_range", "value"),
        Output("textarea_2_price_avg", "value"),
    ],
    [
        Input(component_id="select_category", component_property="value"),
        Input(component_id="select_main_category", component_property="value"),
        Input(component_id="date_slider", component_property="value"),
        Input(component_id="select_region", component_property="value"),
        Input(component_id="crop_price_trend", component_property="clickData"),
    ],
)
def update_graph(
    selected_category, selected_main_category, slider_date, selected_region, click_data
):
    """
    Args:
    select_category : User's selected category.
    select_main_category : User's selected main category
    slider_date : User's slected date (month) through the slider
    select_region: User's selected region. By default the value is none,
                where the users will see all regions and markets in the map.

    Returns:
    fig_map: The map plot figure
    fig_trend: The time series plot in Philippines region
    textarea_1: User's selected date in dateslider
    textarea_2_category: User's selected_category, which is the same as the input of select_category
    textarea_2_category: User's selected_category, which is the same as the input of select_category
    """

    # filter the user's selected category and region
    dff = df[df["Category"] == selected_category]
    dff = (
        dff.copy()
        if selected_region in (None, [])
        else dff[dff["Region"].isin(selected_region)]
    )

    # filter the date that the user chooses in date_slider
    # the data will be used in the map
    # df_map_market means the data will be used to plot the heat map with all market listed in the markers
    df_map_market = (
        dff[dff["Date"].dt.month == date_range[slider_date].month]
        if slider_date != months
        else dff.copy()
    )
    df_map_market["Date"] = df_map_market["Date"].dt.strftime("%Y-%m-%d")

    # df_map_region will generalise the data in a region by the markets in it
    df_map_region = (
        df_map_market.groupby(["Date", "Region"])["Price"]
        .aggregate(["max", "mean", "min"])
        .reset_index()
    )
    df_map_region = df_map_region.rename(
        columns=dict(max="Maximum Price", mean="Average Price", min="Minimum Price")
    )
    df_map_region["Average Price"] = np.round(df_map_region["Average Price"], 1)

    # For all date slider selection, only the latest date will be chosen
    df_map_region = df_map_region.drop_duplicates(["Region"], keep="last")
    df_map_market = df_map_market.drop_duplicates(["Market"], keep="last")

    # dataset prepared to plot the time series of the price trend in selected region
    # by default, selected_region is empty, all regions will be plotted, if selected_region has value, some regions will be filtered
    # parameters set to style the plot
    if selected_region not in ([], None):
        df_trend = (
            dff.groupby(["Category", "Region", "Date"])["Price"]
            .aggregate(["max", "mean", "min"])
            .reset_index()
        )

        zoom_range = 6
        center_lat = df_map_market["Lat"].mean()
        center_lon = df_map_market["Lon"].mean()
        textarea_region = (", ").join(selected_region)
        marker_size=16

    else:
        df_trend = (
            dff.groupby(["Category", "Date"])["Price"]
            .aggregate(["max", "mean", "min"])
            .reset_index()
        )
        zoom_range = 4.8
        center_lat = 12.8
        center_lon = 122.8
        textarea_region = "Philippine"
        marker_size=10

    textarea_2_category = selected_category

    df_trend = df_trend.rename(
        columns=dict(max="Maximum Price", mean="Average Price", min="Minimum Price")
    )
    df_trend["Average Price"] = np.round(df_trend["Average Price"], 1)

    # ========================================
    # Plot the Price Heat Map (Map box with boundary of region)
    # ========================================
    fig_map = px.choropleth_mapbox(
        data_frame=df_map_region,
        locations="Region",
        color="Average Price",
        custom_data=[
            "Maximum Price",
            "Average Price",
            "Minimum Price",
            "Date",
            "Region",
        ],
        featureidkey="properties.REGION",
        geojson=geojson,
        mapbox_style="carto-positron",
        color_continuous_scale="RdYlGn",
        range_color=[df_map_market["Price"].min(), df_map_market["Price"].max()],
        zoom=zoom_range,
        opacity=0.2,
        center={"lat": center_lat, "lon": center_lon},
    )

    fig_map.update_traces(
        hovertemplate="%{customdata[4]}</b>"
        + "<br>Average price: ₱%{customdata[1]}</br>"
        + "Maximum price: ₱%{customdata[0]}</br>"
        + "Minimum price: ₱%{customdata[2]}</br>"
        + "Date: %{customdata[3]}</br>"
    )

    # ========================================
    # Plot the Price Heat Map (Markers with position of market)
    # ========================================
    fig_map.add_trace(
        go.Scattermapbox(
            lat=df_map_market["Lat"],
            lon=df_map_market["Lon"],
            mode="markers",
            marker=dict(
                size=marker_size,
                color=df_map_market["Price"],
                colorscale="RdYlGn",
                cmin=df_map_market["Price"].min(),
                cmax=df_map_market["Price"].max(),
                opacity=1,
            ),
            line=dict(width=2, color="DarkSlateGrey"),
            
            hovertemplate="%{customdata[0]}<br>"
            + "Price: ₱%{marker.color:.2f}<br>"
            + "Date: %{customdata[2]}<extra></extra>",
            customdata=df_map_market[["Market", "Price", "Date"]],
        )
    )

    fig_map.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"size": 18},
        hoverlabel=dict(font=dict(size=24)),
        coloraxis_colorbar=dict(title="Average price", x=1.1),
    )

    # ========================================
    # Plot the Price Trend Map
    # ========================================
    fig_trend = go.Figure()
    zip_color_traces = zip(
        ["green", "red", "goldenrod"],
        ["Maximum Price", "Minimum Price", "Average Price"],
    )
    # If number of selected_region <= 1, all average, minimum and maximum price will be plotted
    # If number of selected_region > 1, only average price will be plotted
    if selected_region in ([], None) or len(selected_region) == 1:
        for color, trace in zip_color_traces:
            fig_trend.add_trace(
                go.Scatter(
                    x=df_trend["Date"],
                    y=df_trend[trace],
                    name="{} - {}".format(textarea_region, trace),
                    hovertemplate="Date: %{x}<br>"
                    + "Maximum Price: ₱%{customdata[0]:.2f}<br>"
                    + "Minimum Price: ₱%{customdata[1]:.2f}<br>"
                    + "Average Price: ₱%{customdata[2]:.2f}<br>",
                    marker=dict(color=color),
                    opacity=0.5,
                    customdata=df_trend[
                        ["Maximum Price", "Minimum Price", "Average Price"]
                    ].values.tolist(),
                )
            )
    else:
        for region in selected_region:
            df_trend_region = df_trend[df_trend["Region"] == region]
            fig_trend.add_trace(
                go.Scatter(
                    x=df_trend_region["Date"],
                    y=df_trend_region["Average Price"],
                    name="{} - {}".format(region, "Average Price"),
                    hovertemplate="Date: %{x}<br>"
                    + "Maximum Price: ₱%{customdata[0]:.2f}<br>"
                    + "Minimum Price: ₱%{customdata[1]:.2f}<br>"
                    + "Average Price: ₱%{customdata[2]:.2f}<br>",
                    opacity=0.5,
                    customdata=df_trend_region[
                        ["Maximum Price", "Minimum Price", "Average Price"]
                    ].values.tolist(),
                )
            )

    fig_trend.update_layout(
        legend=legend_layout,
        yaxis=dict(title="Price", fixedrange=True),
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="backward"),
                    ]
                )
            ),
            rangeslider=dict(
                visible=True,
                thickness=0.05,
            ),
            type="date",
        ),
        margin=dict(l=30, r=30, t=20, b=150),
        plot_bgcolor="rgba(245, 245, 245, 1)",
        paper_bgcolor="rgba(200,200, 200, 0)",
        font={"size": 24},
        hoverlabel=dict(font=dict(size=24)),
    )

    # ========================================
    # Define the text area words
    # ========================================
    if not df_trend.empty:
        if click_data:
            clicked_date = pd.to_datetime(click_data["points"][0]["x"])
            textarea_2_date = clicked_date.strftime("%d %b, %Y")
            df_trend_hover_click = df_trend[df_trend["Date"] == textarea_2_date]

            if selected_region not in ([], None) and len(selected_region) != 1:
                clicked_region = df_trend_hover_click["Region"].values[0]
                df_trend_hover_click = df_trend_hover_click[
                    df_trend_hover_click["Region"] == clicked_region
                ]

            if not df_trend_hover_click.empty:
                textarea_2_price_range = "Price range: ₱{} - ₱{}".format(
                    df_trend_hover_click["Minimum Price"].values[0],
                    df_trend_hover_click["Maximum Price"].values[0],
                )
                textarea_2_price_avg = "Average: ₱{}".format(
                    df_trend_hover_click["Average Price"].values[0]
                )
            else:
                textarea_2_price_range = ""
                textarea_2_price_avg = ""
        else:
            last_row = df_trend.tail(1)
            if not last_row.empty:
                textarea_2_price_range = "Price range: ₱{} - ₱{}".format(
                    last_row["Minimum Price"].values[0],
                    last_row["Maximum Price"].values[0],
                )
                textarea_2_price_avg = "Average: ₱{}".format(
                    last_row["Average Price"].values[0]
                )
                textarea_2_date = (
                    last_row["Date"].dt.strftime("%d %b, %Y").to_string(index=False)
                )
            else:
                textarea_2_date = ""
                textarea_2_price_range = ""
                textarea_2_price_avg = ""
    else:
        textarea_2_date = ""
        textarea_2_price_range = ""
        textarea_2_price_avg = ""

    # try:
    #     xrange = [df_trend[-7], df_trend["Date"][-1]]
    # except:
    #     xrange = None

    # fig_trend.update_xaxes(range=xrange)

    textarea_1 = date_slider_dict[slider_date]

    return (
        fig_map,
        fig_trend,
        textarea_1,
        textarea_2_category,
        textarea_2_date,
        textarea_2_price_range,
        textarea_2_price_avg,
    )


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)

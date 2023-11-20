# Import python packages
import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col


@st.cache_data
def load_data() -> pd.DataFrame:
    data = session.table("STREAMLIT_WIFI.BLOG.WIFI_ON_ICE2").filter(col('DATARATE_PAX_CATEGORY') != 'no value')
    return data.to_pandas()


def get_pydeck_layers(df_route: pd.DataFrame) -> dict:
    lon = "GPS_LAENGE"  # Longitude
    lat = "GPS_BREITE"  # Latitude
    lon_lag = "GPS_LAENGE_LAGGED"  # Longitude of previous measurements
    lat_lag = "GPS_BREITE_LAGGED"  # Latitude of previous measurements

    return {
        "Internet Speed": pdk.Layer(
            "LineLayer",
            data=df_route[:],
            get_target_position=[lon_lag, lat_lag],
            get_source_position=[lon, lat],
            get_color="DATARATE_PAX_COLOR",
            get_width=5,
            opacity=.5,
            pickable=True,
        ),
        "Amount Devices": pdk.Layer(
            "ColumnLayer",
            data=df_route,
            get_position=[lon, lat],
            get_elevation="PAX_AUTH",
            elevation_scale=150,
            extruded=True,
            radius=1750,
            get_fill_color=[0, 128, 255],
            auto_highlight=True,
        ),
        "Wifi Disruptions": pdk.Layer(
            "ArcLayer",
            data=df_route,
            opacity=0.5,
            get_source_position=[lon_lag, lat_lag],
            get_target_position=[lon, lat],
            get_source_color=[255, 0, 0],
            get_target_color=[255, 128, 0],
            get_width="WLAN_DISRUPTION*15",
            pickable=True,
        ),
    }


def plot_activites_route(df_route: pd.DataFrame) -> None:
    # Add subheader
    st.subheader('💻 Explore *WIFI on ICE* enabled activities for your route')

    # Sum minutes for each activity group
    df_activity = pd.DataFrame(
        df_route.groupby(['DATARATE_PAX_ACTIVITY']).agg({
            'TIME_DIFF': lambda x: x.sum() / 60  # transform seconds to minutes
        })).reset_index()
    df_activity["GROUP"] = 0

    # Prepare plotly bar chart
    fig = px.bar(
        df_activity,
        y="GROUP",
        x="TIME_DIFF",
        color="DATARATE_PAX_ACTIVITY",
        color_discrete_map={
            "Text communication (emails, chats), web browsing (text)": "#FF2B2B",
            "Music streaming, web browsing (images), online document editing": "#FF8C3A",
            "HD video streaming, video calls, web browsing (images and videos)": "#8661CC",
            "4K video streaming, online gaming": "#418FD8",
            "Large scale data transfers": "#4EC273",
            "no value": "#FFFFFF"
        },
        category_orders={
            "DATARATE_PAX_ACTIVITY": [
                "Text communication (emails, chats), web browsing (text)",
                "Music streaming, web browsing (images), online document editing",
                "HD video streaming, video calls, web browsing (images and videos)",
                "4K video streaming, online gaming",
                "Large scale data transfers"
            ],
        },
        orientation="h",
        labels={
            "DATARATE_PAX_ACTIVITY": "Activites",
            "TIME_DIFF": "Minutes"

        },
        title="Activities summed in minutes",
        width=700,
        height=320
    )
    fig.update_yaxes(showticklabels=False, title=None)
    fig.update_traces(width=.5)

    # Adjust position of legend
    fig.update_layout(legend=dict(
        # orientation="h",
        yanchor="bottom",
        y=-2,
        xanchor="left",
        x=0
    ))
    # Plot plotly chart in Streamlit
    st.plotly_chart(fig)


def plot_map_route(df_route: pd.DataFrame) -> None:
    st.subheader('🌍 Explore *WIFI on ICE* quality for your route')

    # Display an interactive map to visualize average datarate, amount of devices, and wlan disruptions
    st.caption("Map Layers")
    cols = st.columns(3)
    layers = get_pydeck_layers(df_route)

    # Collect clicked layers
    selected_layers = [layer
                       for i, (layer_name, layer) in enumerate(layers.items())
                       if cols[i].checkbox(layer_name, True)
                       ]

    # Plot layers on map
    if selected_layers:
        st.pydeck_chart(
            pdk.Deck(
                map_style=None,
                initial_view_state={
                    "latitude": 51.1642292,
                    "longitude": 10.4541194,
                    "zoom": 4.5,
                    "pitch": 35.5,
                },
                layers=selected_layers,
                tooltip={"html": "<b>Avergae Datarate: </b> {DATARATE_PAX} <br />"
                                 "<b>Average Datarate per Device: </b> {DATARATE_PAX_CATEGORY} <br />"
                                 "<b>Average Devices amount: </b>{PAX_AUTH} <br />"
                         },
            )
        )
    else:
        st.error("Please choose at least one layer above.")


def get_explanation() -> None:
    with st.expander("ℹ️ See further information"):
        st.write(
            """
            The Deutsche Bahn conducted  measurements in spring 2017 on 3 days across
            its entire long-distance rail network to determine the number of
            devices logged into the train's Wi-Fi and the data rates received
            and sent by the train (in bytes per second). This dataset has been published 
            on [Open-Data Portal](https://data.deutschebahn.com/dataset/wifi-on-ice.html).
    
            For the presented visualiuations, the average data traffic per device has been
            caluclated by dividing the total sent and received data rates of a route taken 
            by a train by the number of devices authenticated in the Wi-Fi.
            The bytes per second have been converted into bits per second. 
    
            Finally, these results are categorized according to the computed data traffic in 
            surf speed categories and respective internet based activites: 
            - :red[very low surf speed], 0-5 MBit/s, 
            - :orange[low surf speed], 5-10 MBit/s, 
            - :violet[medium surf speed], 10-25 MBit/s,
            - :blue[fast surf speed], 25-60 MBit/s, 
            - :green[very fast surf speed], >60 MBit/s, 
            """
        )


def hex_to_rgb(value: float) -> tuple(int, int, int):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


if __name__ == "__main__":
    # Get the current credentials
    session = get_active_session()

    # Write title of the app
    st.title("🚆 WIFI on ICE")
    st.header("Making the most of your journey utilizing onboard Wi-Fi")

    # Load and cache data
    df = load_data()

    # Transform HEX color values to RGB
    df["DATARATE_PAX_COLOR"] = df["DATARATE_PAX_COLOR"].apply(hex_to_rgb)

    # Provide multiselect for exploring specific routes
    example_routes = [
        'Berlin Südkreuz (Vorortbahn) -> München-Laim Pbf',
        'Berlin Hauptbahnhof - Lehrter Bf S-Bahn -> Köln Bbf',
        'Berlin Südende -> Hamburg-Altona',
        'Berlin Südkreuz (Vorortbahn) -> Hildesheim Hbf'

    ]
    route = st.multiselect(
        "Choose a route", sorted(df["ROUTE"].unique()), example_routes
    )
    st.markdown("___")
    df_route = df[df["ROUTE"].isin(route)]

    # Display route specific data
    # Wifi activities in minutes
    with st.container():
        plot_activites_route(df_route)

    # Wifi conditions on a map
    with st.container():
        plot_map_route(df_route)
        get_explanation()

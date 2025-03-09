import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json


st.set_page_config(page_title="Komoditi di Nusa Tenggara Timur", layout="wide")

# App Title
APP_TITLE = "Komoditi di Nusa Tenggara Timur"
APP_SUB_TITLE = "Visualisasi Komoditas per Kabupaten di NTT"

# Load Data
@st.cache_data
def load_data():
    return pd.read_excel("data/Komoditi NTT.xlsx")

@st.cache_data
def load_geojson():
    with open("data/geojson/NTT.geojson", "r", encoding="utf-8") as f:
        geojson_raw = json.load(f)
    return geojson_raw 

# Display Filters
def display_filters(df):
    commodity_list = sorted(df["Komoditi"].unique())
    return st.selectbox("Pilih Komoditi", commodity_list)

# Add Produksi data to GeoJSON features
def add_produksi_to_geojson(geojson_data, filtered_df):
    for feature in geojson_data["features"]:
        regency = feature["properties"]["WADMKK"]
        produksi = filtered_df[filtered_df["Kabupaten"] == regency]["Produksi"].values
        if len(produksi) > 0:
            feature["properties"]["Produksi"] = int(produksi[0])
        else:
            feature["properties"]["Produksi"] = "N/A"  
    return geojson_data

def display_map(filtered_df, geojson_data):
    selected_regions = filtered_df["Kabupaten"].unique()

    geojson_data = add_produksi_to_geojson(geojson_data, filtered_df)

    map_ = folium.Map(location=[-9.601258, 121.800591], zoom_start=7)

    def style_function(feature):
        regency = feature["properties"]["WADMKK"]
        if regency in selected_regions:
            return {"fillColor": "orange", "color": "red", "weight": 3, "fillOpacity": 0.5}
        return {"fillColor": "none", "color": "blue", "weight": 2}

    folium.GeoJson(
        geojson_data,
        name="NTT Regencies",
        tooltip=folium.GeoJsonTooltip(
            fields=["WADMKK", "Produksi"],  
            aliases=["Kabupaten:", "Produksi:"], 
            localize=True,
            sticky=True
        ),
        style_function=style_function
    ).add_to(map_)

    st_folium(map_, width=700, height=500)

def main():
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    df = load_data()
    geojson_data = load_geojson()

    if "filtered_df" not in st.session_state:
        st.session_state.filtered_df = df 

    selected_commodity = display_filters(df)

    if "selected_commodity" not in st.session_state or st.session_state.selected_commodity != selected_commodity:
        st.session_state.filtered_df = df[df["Komoditi"] == selected_commodity]
        st.session_state.selected_commodity = selected_commodity

    col1, col2 = st.columns(2)
    with col1:
        display_map(st.session_state.filtered_df, geojson_data)
    with col2:
        # st.dataframe(st.session_state.filtered_df)
        st.write(f"Kabupaten/Kota Sentra Produksi: {st.session_state.filtered_df['Kabupaten'].iloc[0]}")
        st.write(f"Total Produksi {selected_commodity}: {st.session_state.filtered_df['Produksi'].sum()} ton")  
        st.write(f"Indeks Kesulitan Geografis {st.session_state.filtered_df['Kabupaten'].iloc[0]}: {st.session_state.filtered_df['Range Indeks Kesulitan Geografis Bawah'].iloc[0]} - {st.session_state.filtered_df['Range Indeks Kesulitan Geografis Atas'].iloc[0]}")

if __name__ == "__main__":
    main()
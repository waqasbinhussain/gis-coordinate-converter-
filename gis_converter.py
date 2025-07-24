import zipfile
import io
import streamlit as st
import pandas as pd
from pyproj import Transformer
import folium
from streamlit_folium import st_folium
import re

# Supported Coordinate Systems
CRS_OPTIONS = {
    "WGS84 (Lat/Lon, EPSG:4326)": "EPSG:4326",
    "Web Mercator (EPSG:3857)": "EPSG:3857",
    "UTM Zone 38N (EPSG:32638)": "EPSG:32638",
    "QND95 / Qatar National Grid (EPSG:28600)": "EPSG:28600"
}

st.set_page_config(page_title="GIS Coordinate Converter", layout="centered")
st.title("GIS Coordinate Converter")

# CRS selection
input_label = st.selectbox("Input CRS", list(CRS_OPTIONS.keys()))
input_crs = CRS_OPTIONS[input_label]

output_label = st.selectbox("Output CRS", list(CRS_OPTIONS.keys()))
output_crs = CRS_OPTIONS[output_label]

st.divider()

# Function to convert DMS string to decimal degrees
def dms_to_dd(dms_str):
    match = re.match(r"(\d+)[^\d]+(\d+)[^\d]+([\d\.]+)\"?([NSEW]?)", dms_str.strip())
    if not match:
        return None
    degrees, minutes, seconds, direction = match.groups()
    dd = float(degrees) + float(minutes)/60 + float(seconds)/3600
    if direction in ['S', 'W']:
        dd = -dd
    return dd

# Convert safely: handle both decimal and DMS
def parse_coordinate(value):
    try:
        return float(value)
    except:
        return dms_to_dd(str(value))

# --- Single Point Conversion ---
st.markdown("### Convert a Single Coordinate")
col1, col2 = st.columns(2)
with col1:
    x = st.text_input("Longitude / Easting (X)", value="51.531", help="Supports Decimal Degrees or DMS format like 51°36'25.0\"E")
with col2:
    y = st.text_input("Latitude / Northing (Y)", value="25.285", help="Supports Decimal Degrees or DMS format like 25°10'24.17\"N")

if st.button("Convert Single Point", key="convert_single_btn"):
    try:
        x_parsed = parse_coordinate(x)
        y_parsed = parse_coordinate(y)
        transformer = Transformer.from_crs(input_crs, output_crs, always_xy=True)
        x_out, y_out = transformer.transform(x_parsed, y_parsed)
        st.session_state["converted"] = True
        st.session_state["x_in"] = x_parsed
        st.session_state["y_in"] = y_parsed
        st.session_state["x_out"] = x_out
        st.session_state["y_out"] = y_out
    except Exception as e:
        st.error(f"Conversion Error: {e}")
        st.session_state["converted"] = False

if st.session_state.get("converted"):
    st.success("Converted Successfully")
    st.code(f"Converted X: {st.session_state['x_out']:.6f}, Y: {st.session_state['y_out']:.6f}")
    st.markdown("### Map View")
    try:
        m = folium.Map(location=[st.session_state["y_in"], st.session_state["x_in"]], zoom_start=13)
        folium.Marker([st.session_state["y_in"], st.session_state["x_in"]],
                      popup="Original (Input)", tooltip="Input Point",
                      icon=folium.Icon(color="blue")).add_to(m)
        folium.Marker([st.session_state["y_out"], st.session_state["x_out"]],
                      popup="Converted (Output)", tooltip="Converted Point",
                      icon=folium.Icon(color="green")).add_to(m)
        st_folium(m, width=700, height=500)
    except Exception as e:
        st.warning(f"Map preview failed: {e}")

st.divider()

# --- CSV Upload Conversion ---
st.markdown("### Upload a CSV File with Columns: Location_Name, x, y")
st.markdown("*Note: The x and y values can be in either Decimal Degrees or DMS format like `51°36'25.0\"N`, `25°10'24.17\"N`*")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if "csv_converted" not in st.session_state:
    st.session_state["csv_converted"] = False
if "csv_df" not in st.session_state:
    st.session_state["csv_df"] = None

if uploaded_file:
    try:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
            if df.empty or df.columns.size == 1:
                raise ValueError("Empty or malformed CSV")
        except Exception:
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                if df.empty or df.columns.size == 1:
                    raise ValueError("Empty or malformed CSV")
            except Exception:
                df = pd.read_csv(uploaded_file, encoding='ISO-8859-1', sep=',', on_bad_lines='skip', engine='python')
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")

if st.session_state["csv_converted"] and st.session_state["csv_df"] is not None:
    df = st.session_state["csv_df"]
    st.success("CSV Converted Successfully")
    st.dataframe(df)

    csv_out = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Converted CSV", csv_out,
                       file_name="converted_coordinates.csv", mime='text/csv')

    try:
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom.minidom import parseString

        kml = Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        doc = SubElement(kml, 'Document')

        for i, row in df.iterrows():
            placemark = SubElement(doc, 'Placemark')
            name = SubElement(placemark, 'name')
            name.text = str(row['Location_Name'])

            description = SubElement(placemark, 'description')
            description.text = f"Converted X: {str(row['x_converted'])}, Y: {str(row['y_converted'])}"

            point = SubElement(placemark, 'Point')
            coordinates = SubElement(point, 'coordinates')
            coordinates.text = f"{str(row['lon_wgs'])},{str(row['lat_wgs'])},0"

        kml_str = tostring(kml)
        pretty_kml = parseString(kml_str).toprettyxml(indent="  ")
        kml_filename = "converted_points.kml"

        kmz_buffer = io.BytesIO()
        with zipfile.ZipFile(kmz_buffer, 'w', zipfile.ZIP_DEFLATED) as kmz:
            kmz.writestr(kml_filename, pretty_kml)

        st.download_button("Export as KMZ for Google Earth", data=kmz_buffer.getvalue(),
                           file_name="converted_points.kmz", mime="application/vnd.google-earth.kmz")
    except Exception as e:
        st.warning(f"Could not generate KMZ: {e}")

    st.markdown("### Map View of Converted Points (WGS84)")
    try:
        m = folium.Map(location=[df['lat_wgs'].iloc[0], df['lon_wgs'].iloc[0]], zoom_start=10)
        for i, row in df.iterrows():
            folium.Marker(
                [row['lat_wgs'], row['lon_wgs']],
                tooltip=row['Location_Name'],
                popup=f"{row['Location_Name']}\nX: {row['x_converted']:.5f}, Y: {row['y_converted']:.5f}",
                icon=folium.Icon(color="green", icon="ok-sign"),
            ).add_to(m)
        st_folium(m, width=700, height=500)
    except Exception as e:
        st.warning(f"Could not display map: {e}")

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Developed by <b>Waqas Bin Hussain</b><br>"
    "<a href='https://www.linkedin.com/in/waqasbinhussain/' target='_blank' style='text-decoration: none; color: #0a66c2;'>Connect on LinkedIn</a></p>",
    unsafe_allow_html=True
)

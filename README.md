# GIS Coordinate Converter - Documentation

## 📌 Project Overview

This project is a user-friendly GIS coordinate conversion tool built using Python and Streamlit. It enables users to convert coordinates between different geographic systems (notably WGS84 and QND95), visualize the locations on an interactive map, and download the results in both CSV and KMZ formats for use in tools like Google Earth.

---

## 🛠 Technologies & Libraries Used

| Library                                    | Purpose                                     |
| ------------------------------------------ | ------------------------------------------- |
| `streamlit`                                | Web-based UI rendering and interactivity    |
| `pyproj`                                   | Coordinate transformation using EPSG codes  |
| `pandas`                                   | CSV handling and tabular data processing    |
| `folium`                                   | Interactive map rendering                   |
| `streamlit-folium`                         | Streamlit wrapper for embedding Folium maps |
| `zipfile`                                  | Creation of KMZ (zipped KML) export         |
| `io`                                       | In-memory stream handling for KMZ files     |
| `xml.etree.ElementTree`, `xml.dom.minidom` | XML construction for KML formatting         |

---

## ⚙️ App Features & Workflow

### 1. **User Interface via Streamlit**

- A simple web UI is rendered using Streamlit where users can:
  - Select input and output coordinate systems (CRS)
  - Enter single coordinate point for quick conversion
  - Upload CSV file containing batch coordinates for conversion
  - View results in a table and interactive map
  - Download results as `.csv` or `.kmz`

### 2. **CRS Selection**

- Options provided in a dropdown:
  ```python
  CRS_OPTIONS = {
      "WGS84 (Lat/Lon, EPSG:4326)": "EPSG:4326",
      "Web Mercator (EPSG:3857)": "EPSG:3857",
      "UTM Zone 38N (EPSG:32638)": "EPSG:32638",
      "QND95 / Qatar National Grid (EPSG:28600)": "EPSG:28600"
  }
  ```

### 3. **Single Coordinate Conversion**

- Users input X (longitude) and Y (latitude), then click a button to convert.
- The app uses `pyproj.Transformer.from_crs` to perform the transformation.
- The result is displayed and also shown on a Folium map.

### 4. **CSV Batch Upload**

- CSV format: `Location_Name, x, y`
- Once uploaded, the user must click "Convert Now" to trigger conversion.
- Converted data includes:
  - Original columns
  - Converted X/Y coordinates
  - WGS84 lat/lon for map rendering
- Output is available as:
  - 📁 CSV download
  - 🌍 KMZ download (Google Earth compatible)

### 5. **Map Rendering (Folium)**

- Map centers on the first coordinate
- For each point:
  - A marker is added with popup & tooltip showing location name and converted coordinates
- Embedded in the app via `st_folium`

### 6. **KMZ Export**

- Uses `xml.etree.ElementTree` to generate a KML structure
- KML is written into memory
- A `.kmz` file is created using `zipfile.ZipFile` with `.kml` inside
- Downloaded via `st.download_button()`

---

## 📂 File Structure

```
GIS-Coordinate-Converter/
├── gis_converter.py                # Main app
├── requirements.txt               # Python dependencies
├── README.md                      # Project info and usage
```

---

## 📥 Running Locally

```bash
pip install -r requirements.txt
streamlit run gis_converter.py
```

---

## 🙋 Author

Developed by **Waqas Bin Hussain**  
🔗 [LinkedIn Profile](https://www.linkedin.com/in/waqasbinhussain/)

---

## 🚀 Hosting

- Hosted on [Streamlit Cloud](https://share.streamlit.io)
- Live Demo: [https://waqasbinhussain-gis-coordinate-converter.streamlit.app/](https://waqasbinhussain-gis-coordinate-converter.streamlit.app/)

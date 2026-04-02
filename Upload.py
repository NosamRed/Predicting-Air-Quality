import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import threading
import queue
import time
import re
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Configuration
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB default
MAX_ROWS = 50000
CHUNK_SIZE = 1000
REQUIRED_COLUMNS = [
    'AQI Value',
    'CO AQI Value',
    'Ozone AQI Value',
    'NO2 AQI Value',
    'PM2.5 AQI Value',
    'lat',
    'lng'
]

# Geocoder setup
GEOCODER_USER_AGENT = "air_quality_uploader_app"
GEOCODE_DELAY_SECONDS = 1.0
geolocator = Nominatim(user_agent=GEOCODER_USER_AGENT, timeout=10)
_geocode_cache = {}

def canonicalize(colname: str) -> str:
    """Return a normalized canonical form for a header string."""
    if colname is None:
        return ""
    s = str(colname).lower().strip()
    # replace punctuation with space, collapse whitespace
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# Mapping from canonical header -> target column name
HEADER_MAP = {
    # AQI
    'max aqi': 'AQI Value',
    '90th percentile aqi': 'AQI Value',
    'median aqi': 'AQI Value',
    'aqi value': 'AQI Value',
    'aqi': 'AQI Value',

    # CO
    'days co': 'CO AQI Value',
    'co days': 'CO AQI Value',
    'co': 'CO AQI Value',
    'co aqi': 'CO AQI Value',
    'co aqi value': 'CO AQI Value',

    # NO2
    'days no2': 'NO2 AQI Value',
    'no2 days': 'NO2 AQI Value',
    'no2': 'NO2 AQI Value',
    'no2 aqi': 'NO2 AQI Value',

    # Ozone
    'days ozone': 'Ozone AQI Value',
    'ozone days': 'Ozone AQI Value',
    'ozone': 'Ozone AQI Value',
    'ozone aqi': 'Ozone AQI Value',

    # PM2.5
    'days pm2 5': 'PM2.5 AQI Value',
    'days pm25': 'PM2.5 AQI Value',
    'pm2 5': 'PM2.5 AQI Value',
    'pm25': 'PM2.5 AQI Value',
    'pm2.5': 'PM2.5 AQI Value',
    'pm2.5 aqi': 'PM2.5 AQI Value',

    # lat/lng
    'latitude': 'lat',
    'lat': 'lat',
    'longitude': 'lng',
    'lon': 'lng',
    'lng': 'lng',

    # location-like columns
    'cbsa': 'location',
    'cbsa code': 'location',
    'location': 'location',
    'place': 'location',
    'city': 'location',
    'county': 'location',
    'state': 'location'
}

def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize dataframe column names using HEADER_MAP and heuristics.
    Returns a new DataFrame with renamed columns.
    """
    rename_map = {}
    for col in df.columns:
        key = canonicalize(col)
        if key in HEADER_MAP:
            rename_map[col] = HEADER_MAP[key]
        else:
            # heuristic: if header contains 'days' and a pollutant token, map it
            if 'days' in key:
                if 'co' in key:
                    rename_map[col] = 'CO AQI Value'
                elif 'no2' in key:
                    rename_map[col] = 'NO2 AQI Value'
                elif 'ozone' in key:
                    rename_map[col] = 'Ozone AQI Value'
                elif 'pm2' in key or 'pm25' in key:
                    rename_map[col] = 'PM2.5 AQI Value'
            # heuristic: if header contains 'aqi' and a pollutant token
            elif 'aqi' in key:
                if 'co' in key:
                    rename_map[col] = 'CO AQI Value'
                elif 'no2' in key:
                    rename_map[col] = 'NO2 AQI Value'
                elif 'ozone' in key:
                    rename_map[col] = 'Ozone AQI Value'
                elif 'pm2' in key or 'pm25' in key:
                    rename_map[col] = 'PM2.5 AQI Value'
                else:
                    rename_map[col] = 'AQI Value'
            # fallback: numeric-looking columns might be pollutant values; leave as-is
            # otherwise leave column unchanged
    # apply rename
    df = df.rename(columns=rename_map)
    # ensure canonical required columns exist (add with NaN if missing)
    for rc in REQUIRED_COLUMNS + ['location']:
        if rc not in df.columns:
            df[rc] = pd.NA
    return df

def geocode_location(location_str):
    if not location_str or not str(location_str).strip():
        return None
    key = str(location_str).strip()
    if key in _geocode_cache:
        return _geocode_cache[key]
    try:
        time.sleep(GEOCODE_DELAY_SECONDS)
        loc = geolocator.geocode(key)
        if loc:
            coords = (loc.latitude, loc.longitude)
            _geocode_cache[key] = coords
            return coords
        else:
            _geocode_cache[key] = None
            return None
    except (GeocoderTimedOut, GeocoderServiceError):
        return None
    except Exception:
        return None

class UploadFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_file = None
        self.worker_queue = queue.Queue()
        self.create_widgets()
        self.poll_worker_queue()

    def create_widgets(self):
        tk.Label(self, text="Upload Air Quality Data").grid(column=3, pady=20)

        tk.Label(self, text="AQI Value:").grid(row=1, column=0, pady=5)
        self.AQIValue = tk.Entry(self)
        self.AQIValue.grid(row=2, column=0, pady=5)

        tk.Label(self, text="CO Value:").grid(row=1, column=1, pady=5)
        self.COValue = tk.Entry(self)
        self.COValue.grid(row=2, column=1, pady=5)

        tk.Label(self, text="Ozone Value:").grid(row=1, column=2, pady=5)
        self.OzoneValue = tk.Entry(self)
        self.OzoneValue.grid(row=2, column=2, pady=5)

        tk.Label(self, text="NO2 Value:").grid(row=1, column=3, pady=5)
        self.NO2Value = tk.Entry(self)
        self.NO2Value.grid(row=2, column=3, pady=5)

        tk.Label(self, text="PM2.5 Value:").grid(row=1, column=4, pady=5)
        self.PM25Value = tk.Entry(self)
        self.PM25Value.grid(row=2, column=4, pady=5)

        tk.Label(self, text="Latitude:").grid(row=1, column=5, pady=5)
        self.lat = tk.Entry(self)
        self.lat.grid(row=2, column=5, pady=5)

        tk.Label(self, text="Longitude:").grid(row=1, column=6, pady=5)
        self.lng = tk.Entry(self)
        self.lng.grid(row=2, column=6, pady=5)

        tk.Label(self, text="Location name").grid(row=1, column=7, pady=5)
        self.location_name = tk.Entry(self)
        self.location_name.grid(row=2, column=7, pady=5)

        tk.Button(self, text="Upload data (single row)", command=self.upload_data).grid(row=3, column=2, pady=10)
        tk.Button(self, text="Choose CSV to upload", command=self.choose_csv).grid(row=3, column=3, pady=10)
        tk.Button(self, text="Start CSV upload", command=self.start_csv_upload).grid(row=3, column=4, pady=10)

        self.preview_label = tk.Label(self, text="No file selected")
        self.preview_label.grid(row=4, column=0, columnspan=4, sticky='w', pady=(10,0))


    def upload_data(self):
        AQI = self.AQIValue.get().strip()
        CO = self.COValue.get().strip()
        Ozone = self.OzoneValue.get().strip()
        NO2 = self.NO2Value.get().strip()
        PM25 = self.PM25Value.get().strip()
        lat = self.lat.get().strip()
        lng = self.lng.get().strip()
        location = self.location_name.get().strip()

        if (not lat or not lng) and location:
            coords = geocode_location(location)
            if coords:
                lat, lng = str(coords[0]), str(coords[1])
            else:
                messagebox.showwarning("Geocode warning", f"Could not geocode location '{location}'. Please provide lat/lng.")
                return

        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, 'Test.csv')

        new_df = pd.DataFrame({
            'AQI Value': [AQI],
            'CO AQI Value': [CO],
            'Ozone AQI Value': [Ozone],
            'NO2 AQI Value': [NO2],
            'PM2.5 AQI Value': [PM25],
            'lat': [lat],
            'lng': [lng]
        })

        write_header = False
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                if not f.read(1):
                    write_header = True
        except FileNotFoundError:
            write_header = True

        try:
            new_df.to_csv(filename, mode='a', index=False, header=write_header)
            df_check = pd.read_csv(filename)
            messagebox.showinfo("Upload", f"Data uploaded!\nFile: {filename}\nLast row: {df_check.tail(1).to_dict(orient='records')[0]}")
        except Exception as e:
            messagebox.showerror("Upload error", f"Could not write to {filename}:\n{e}")
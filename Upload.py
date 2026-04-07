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
MAX_ROWS = 100000
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

# AQI derivation strategy (keeps raw metrics and derives a single AQI Value)
DERIVATION_STRATEGY = 'prefer_max'  # options: 'prefer_max', 'max_of_available', 'median_of_available'

# Geocoder setup
GEOCODER_USER_AGENT = "air_quality_uploader_app"
GEOCODE_DELAY_SECONDS = 1.0
geolocator = Nominatim(user_agent=GEOCODER_USER_AGENT, timeout=10)
_geocode_cache = {}

def canonicalize(colname: str) -> str:
    if colname is None:
        return ""
    s = str(colname).lower().strip()
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

HEADER_MAP = {
    # AQI variants
    'max aqi': 'AQI_Max',
    '90th percentile aqi': 'AQI_90th',
    'median aqi': 'AQI_Median',
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
    rename_map = {}
    for col in df.columns:
        key = canonicalize(col)
        if key in HEADER_MAP:
            rename_map[col] = HEADER_MAP[key]
        else:
            if 'days' in key:
                if 'co' in key:
                    rename_map[col] = 'CO AQI Value'
                elif 'no2' in key:
                    rename_map[col] = 'NO2 AQI Value'
                elif 'ozone' in key:
                    rename_map[col] = 'Ozone AQI Value'
                elif 'pm2' in key or 'pm25' in key:
                    rename_map[col] = 'PM2.5 AQI Value'
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
    df = df.rename(columns=rename_map)
    # ensure canonical columns exist
    for rc in REQUIRED_COLUMNS + ['location', 'AQI_Max', 'AQI_90th', 'AQI_Median']:
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

def derive_aqi_value(row):
    vals = []
    for col in ('AQI_Max', 'AQI_90th', 'AQI_Median'):
        v = row.get(col)
        try:
            if pd.notna(v):
                vals.append(float(v))
        except Exception:
            pass
    if not vals:
        return pd.NA
    if DERIVATION_STRATEGY == 'prefer_max':
        if pd.notna(row.get('AQI_Max')):
            try:
                return float(row.get('AQI_Max'))
            except Exception:
                pass
        if pd.notna(row.get('AQI_90th')):
            try:
                return float(row.get('AQI_90th'))
            except Exception:
                pass
        try:
            return float(row.get('AQI_Median'))
        except Exception:
            return vals[0]
    if DERIVATION_STRATEGY == 'max_of_available':
        return max(vals)
    if DERIVATION_STRATEGY == 'median_of_available':
        return float(pd.Series(vals).median())
    return vals[0]

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

        controls_row = 3
        tk.Button(self, text="Upload data (single row)", command=self.upload_data).grid(row=controls_row, column=0, pady=10)
        tk.Button(self, text="Choose CSV to upload", command=self.choose_csv).grid(row=controls_row, column=1, pady=10)
        tk.Button(self, text="Start CSV upload", command=self.start_csv_upload).grid(row=controls_row, column=2, pady=10)

        self.preview_label = tk.Label(self, text="No file selected")
        self.preview_label.grid(row=4, column=0, columnspan=4, sticky='w', pady=(10,0))

        self.status_label = tk.Label(self, text="")
        self.status_label.grid(row=6, column=0, columnspan=4, sticky='w')

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

    def choose_csv(self):
        filetypes = [('CSV files', '*.csv'), ('All files', '*.*')]
        path = filedialog.askopenfilename(title='Select CSV file', filetypes=filetypes)
        if not path:
            return
        self.selected_file = path
        self.preview_label.config(text=f"Selected: {os.path.basename(path)}")
        self.preview_csv(path)


    def start_csv_upload(self):
        if not self.selected_file:
            messagebox.showwarning("No file", "Please choose a CSV file first.")
            return
        self.status_label.config(text="Starting upload...", fg='black')
        worker = threading.Thread(target=self._process_csv_worker, args=(self.selected_file,))
        worker.daemon = True
        worker.start()

    def _process_csv_worker(self, path):
        try:
            if not path.lower().endswith('.csv'):
                raise ValueError("File is not a CSV")
            size = os.path.getsize(path)
            if size > MAX_FILE_SIZE_BYTES:
                raise ValueError("File exceeds maximum allowed size")

            total_rows = 0
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for i, _ in enumerate(f, 1):
                    total_rows = i
                    if total_rows > MAX_ROWS:
                        break
            if total_rows == 0:
                raise ValueError("CSV is empty")
            if total_rows > MAX_ROWS:
                raise ValueError(f"CSV has too many rows ({total_rows}). Max allowed is {MAX_ROWS}.")

            reader = pd.read_csv(path, chunksize=CHUNK_SIZE, iterator=True)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            out_filename = os.path.join(script_dir, 'Test.csv')
            write_header = False
            try:
                with open(out_filename, 'r', encoding='utf-8') as f:
                    if not f.read(1):
                        write_header = True
            except FileNotFoundError:
                write_header = True

            processed = 0
            first_chunk = True
            for chunk in reader:
                chunk = normalize_headers(chunk)

                # If location column exists, geocode missing lat/lng
                if 'location' in chunk.columns:
                    loc_col = 'location'
                    # build mask of rows needing geocode
                    if 'lat' in chunk.columns and 'lng' in chunk.columns:
                        need_geo_mask = chunk['lat'].isna() | chunk['lng'].isna()
                    elif 'lat' in chunk.columns:
                        need_geo_mask = chunk['lat'].isna()
                    elif 'lng' in chunk.columns:
                        need_geo_mask = chunk['lng'].isna()
                    else:
                        need_geo_mask = pd.Series([True] * len(chunk), index=chunk.index)

                    to_geocode = chunk.loc[need_geo_mask, loc_col].dropna()
                    for loc_str in to_geocode:
                        geocode_location(loc_str)

                    def fill_coords(row):
                        try:
                            lat_val = row.get('lat', pd.NA)
                            lng_val = row.get('lng', pd.NA)
                            if pd.isna(lat_val) or pd.isna(lng_val):
                                loc = row.get(loc_col)
                                if pd.isna(loc) or not str(loc).strip():
                                    return row
                                coords = _geocode_cache.get(str(loc).strip())
                                if coords:
                                    row['lat'] = coords[0]
                                    row['lng'] = coords[1]
                        except Exception:
                            pass
                        return row

                    chunk = chunk.apply(fill_coords, axis=1)

                # Ensure raw AQI columns exist
                for col in ('AQI_Max', 'AQI_90th', 'AQI_Median'):
                    if col not in chunk.columns:
                        chunk[col] = pd.NA

                # Derive single AQI Value
                chunk['AQI Value'] = chunk.apply(derive_aqi_value, axis=1)

                # Ensure required columns exist (normalize_headers already added them)
                for rc in REQUIRED_COLUMNS:
                    if rc not in chunk.columns:
                        chunk[rc] = pd.NA

                # --- Select and normalize only the canonical output columns ---
                desired_cols = [
                    'AQI Value',
                    'CO AQI Value',
                    'Ozone AQI Value',
                    'NO2 AQI Value',
                    'PM2.5 AQI Value',
                    'lat',
                    'lng'
                ]

                # Make sure all desired columns exist (added above), then coerce types
                out_chunk = chunk.copy()

                # Coerce numeric pollutant/AQI columns to numeric where possible
                for col in ['AQI Value', 'CO AQI Value', 'Ozone AQI Value', 'NO2 AQI Value', 'PM2.5 AQI Value']:
                    if col in out_chunk.columns:
                        out_chunk[col] = pd.to_numeric(out_chunk[col], errors='coerce')

                # Coerce lat/lng to numeric (keep as strings if you prefer)
                for col in ['lat', 'lng']:
                    if col in out_chunk.columns:
                        out_chunk[col] = pd.to_numeric(out_chunk[col], errors='coerce')

                # Keep only the desired columns in the specified order
                out_chunk = out_chunk[desired_cols]

                # Optional: drop rows that are completely empty in the desired columns
                # (uncomment if you want to skip rows with no useful data)
                # out_chunk = out_chunk.dropna(how='all', subset=desired_cols)

                # Append only the selected columns to the output CSV
                out_chunk.to_csv(out_filename, mode='a', index=False, header=write_header)
                write_header = False
                processed += len(out_chunk)


            # signal completion
            self.worker_queue.put(('done', out_filename, processed))
        except Exception as e:
            self.worker_queue.put(('error', str(e)))

    def poll_worker_queue(self):
        try:
            while True:
                item = self.worker_queue.get_nowait()
                if not item:
                    continue
                tag = item[0]
                if tag == 'done':
                    out_filename, processed = item[1], item[2]
                    self.status_label.config(text=f"Upload complete. Appended {processed} rows to {out_filename}", fg='green')
                    messagebox.showinfo("Upload complete", f"Appended {processed} rows to {out_filename}")
                    self.selected_file = None
                    self.preview_label.config(text="No file selected")
                elif tag == 'error':
                    err = item[1]
                    self.status_label.config(text=f"Error: {err}", fg='red')
                    messagebox.showerror("Upload error", f"CSV upload failed:\n{err}")
        except queue.Empty:
            pass
        self.after(200, self.poll_worker_queue)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Air Quality Uploader")
    frame = UploadFrame(root)
    frame.pack(padx=10, pady=10)
    root.mainloop()
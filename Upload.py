import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os

class UploadFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        

    #Makes the design for the upload page
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

        tk.Button(self, text="Upload data", command=self.upload_data).grid(row=3, column=3, pady=10)


    #Allows the Upload button to work
    def upload_data(self):  

        AQI = self.AQIValue.get().strip()
        CO = self.COValue.get().strip()
        Ozone = self.OzoneValue.get().strip()
        NO2 = self.NO2Value.get().strip()
        PM25 = self.PM25Value.get().strip()
        lat = self.lat.get().strip()
        lng = self.lng.get().strip()

        # ensure Test.csv is in the same folder as this script
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

        # write header only if file missing or empty
        write_header = False
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                if not f.read(1):
                    write_header = True
        except FileNotFoundError:
            write_header = True

        try:
            new_df.to_csv(filename, mode='a', index=False, header=write_header)
            # quick verification
            df_check = pd.read_csv(filename)
            messagebox.showinfo("Upload",
                f"Data uploaded!\nFile: {filename}\nLast row: {df_check.tail(1).to_dict(orient='records')[0]}")
        except Exception as e:
            messagebox.showerror("Upload error", f"Could not write to {filename}:\n{e}")
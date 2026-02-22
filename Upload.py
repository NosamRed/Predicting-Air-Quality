import tkinter as tk
from tkinter import messagebox
import pandas as pd

class UploadFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

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


    def upload_data(self):
        AQI = self.AQIValue.get()
        CO= self.COValue.get()
        Ozone = self.OzoneValue.get()
        NO2 = self.NO2Value.get()
        PM25 = self.PM25Value.get()
        lng = self.lng.get()
        lat = self.lat.get()

        import pandas as pd

        df = pd.read_csv('Test.csv')
        df = pd.DataFrame({
            'AQI Value': [AQI],
            'CO AQI Value': [CO],
            'Ozone AQI Value': [Ozone],
            'NO2 AQI Value': [NO2],
            'PM2.5 AQI Value': [PM25],
            'lat': [lat],
            'lng': [lng]
        })
        df = pd.concat([df, df], ignore_index=True)
        df.to_csv('Test.csv', index=False)

        
        messagebox.showinfo("Upload", "Data uploaded successfully!")
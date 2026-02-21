import tkinter as tk
from tkinter import messagebox

class UploadFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Upload Air Quality Data").pack(pady=20)

        tk.Label(self, text="AQI Value:").pack(pady=5)
        self.AQIValue = tk.Entry(self).pack(pady=5)


        tk.Label(self, text="CO Value:").pack(pady=5)
        self.COValue = tk.Entry(self).pack(pady=5)


        tk.Label(self, text="Ozone Value:").pack(pady=5)
        self.OzoneValue = tk.Entry(self).pack(pady=5)


        tk.Label(self, text="NO2 Value:").pack(pady=5)
        self.NO2Value = tk.Entry(self).pack(pady=5)


        tk.Label(self, text="PM2.5 Value:").pack(pady=5)
        self.PM25Value = tk.Entry(self).pack(pady=5)


        tk.Label(self, text="Latitude:").pack(pady=5)
        self.lat = tk.Entry(self).pack(pady=5)


        tk.Label(self, text="Longitude:").pack(pady=5)
        self.lng = tk.Entry(self).pack(pady=5)


        tk.Button(self, text="Upload data", command=self.upload_data).pack(pady=10)


    def upload_data(self):
        # Placeholder for file upload logic
        messagebox.showinfo("Upload", "Data uploaded successfully!")
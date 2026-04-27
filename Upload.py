import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil


class UploadFrame(tk.Frame):
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent)
        self.refresh_callback = refresh_callback
        self.create_widgets()

    def create_widgets(self):
        tk.Label(
            self,
            text="Upload Air Quality CSV File",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=20)

        tk.Button(
            self,
            text="Choose CSV File",
            command=self.upload_csv,
            width=25
        ).pack(pady=20)

    def upload_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv")]
        )

        if not file_path:
            return

        script_dir = os.path.dirname(os.path.abspath(__file__))
        saved_path = os.path.join(script_dir, "uploaded_data.csv")

        try:
            shutil.copy(file_path, saved_path)

            messagebox.showinfo(
                "Upload Complete",
                "CSV uploaded successfully!"
            )

            if self.refresh_callback:
                self.refresh_callback(saved_path)

        except Exception as e:
            messagebox.showerror(
                "Upload Error",
                f"Could not upload CSV:\n{e}"
            )
import tkinter as tk


class InfoFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

#Makes the design for the info page
    def create_widgets(self):
        tk.Label(self, text="Developers:", font=("Segoe UI", 12, "bold")).grid(column=0, pady=20)

        #Our Names
        tk.Label(self, text="Calvin Silvers").grid(row=1, column=5, pady=5)
        tk.Label(self, text="Mason Lyons").grid(row=2, column=5, pady=5)
        tk.Label(self, text="Melvin Augustin").grid(row=3, column=5, pady=5)
        tk.Label(self, text="Michael Miller").grid(row=4, column=5, pady=5)

        #Button to close the window
        tk.Button(self, text="Close", command=self.close_window).grid(row=8, column=5, pady=10)

#Code for close button to work
    def close_window(self):
        self.master.destroy()
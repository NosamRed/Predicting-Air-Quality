import tkinter as tk


class InfoFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

#Makes the design for the info page
    def create_widgets(self):
        tk.Label(self, text="Developers:", font=("Segoe UI", 12, "bold")).grid(row=0,column=0, pady=20)

        #Our Names
        tk.Label(self, text="Calvin Silvers:").grid(row=1, column=2, pady=5)
        tk.Label(self, text="Mason Lyons:").grid(row=2, column=2, pady=5)
        tk.Label(self, text="Melvin Augustin:").grid(row=3, column=2, pady=5)
        tk.Label(self, text="Michael Miller:").grid(row=4, column=2, pady=5)

        #Our Emails
        tk.Label(self, text="csilve05@rams.shepherd.edu").grid(row=1, column=3, pady=5)
        tk.Label(self, text="mlyons03@rams.shepherd.edu").grid(row=2, column=3, pady=5)
        tk.Label(self, text="maugus02@rams.shepherd.edu").grid(row=3, column=3, pady=5)
        tk.Label(self, text="mmille42@rams.shepherd.edu").grid(row=4, column=3, pady=5)

        #Project Description
        tk.Label(self, text="Project Description:", font=("Segoe UI", 12, "bold")).grid(row=6, column=0, pady=20)
        tk.Label(self, text="This is a program made to calculate and predict what the air quality will be in any given location.").grid(row=7, column=0, columnspan=7, pady=5)

        #Button to close the window
        tk.Button(self, text="Close", command=self.close_window).grid(row=8, column=2, pady=10)

#Code for close button to work
    def close_window(self):
        self.master.destroy()
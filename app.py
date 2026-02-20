import tkinter as tk
from tkinter import ttk
from tkinter import Canvas
import matplotlib
import matplotlib.pyplot as plt 
import numpy as np



# ---------------------------------------------
# COLORS & THEME (Static Prototype)
# ---------------------------------------------
BG = "#F5F7FA"
LIGHT_GRAY = "#C7CBD3"
BAR_GRAY = "#CCD7EC"
DARK_BG = "#1F2937"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#111827"
TEXT_LIGHT = "#6B7280"
GREEN = "#22C55E"
YELLOW = "#EAB308"
ORANGE = "#F97316"
RED = "#EF4444"

# ---------------------------------------------
# MAIN WINDOW
# ---------------------------------------------
root = tk.Tk()
root.title("Air Quality Dashboard")
root.geometry("1200x800")
root.configure(bg=BG)
icon = tk.PhotoImage(file="FunnyMEME.png")  # Ensure you have an icon.png in the same directory
root.iconphoto(True, icon)


# ---------------------------------------------
# CARD CREATOR
# ---------------------------------------------
def create_card(parent, row, col, width=300, height=150):
    frame = tk.Frame(parent, bg=CARD_BG, bd=0, relief="flat")
    frame.grid(row=row, column=col, padx=15, pady=15, sticky="nw")
    frame.grid_propagate(True)
    frame.config(width=width, height=height)
    return frame

# ---------------------------------------------
# TITLE BAR
# ---------------------------------------------
title_frame = tk.Frame(root, bg=BG)
title_frame.pack(fill="x", padx=20, pady=10)

title_label = tk.Label(
    title_frame, 
    text="Air Quality Index", 
    font=("Segoe UI", 20, "bold"), 
    bg=BG, 
    fg=TEXT_DARK
)
title_label.pack(side="left")

upload_button = tk.Button(title_frame, text="Upload Data", bg=LIGHT_GRAY, fg=TEXT_DARK, font=("Segoe UI", 10), bd=0, relief="flat")
upload_button.pack(side="right", padx=10)

login_button = tk.Button(title_frame, text="Login", bg=GREEN, fg="white", font=("Segoe UI", 10, "bold"), bd=0, relief="flat")
login_button.pack(side="right", padx=10)

# ---------------------------------------------
# MAIN GRID
# ---------------------------------------------
main_frame = tk.Frame(root, bg=LIGHT_GRAY)
main_frame.pack(fill="both", expand=1)

my_canvas = Canvas(main_frame , bg=LIGHT_GRAY, )
my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
#-----------------------------------------------
#Scrollbar
#----------------------------------------------
my_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=my_canvas.yview)
my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

seconframe = tk.Frame(my_canvas, bg=LIGHT_GRAY)
my_canvas.create_window((0,0), window=seconframe, anchor="nw")




# ---------------------------------------------
# CARD 1: MAIN AQI GAUGE (Static)
# ---------------------------------------------
card1 = create_card(seconframe, 0, 0, 700, 250)

title = tk.Label(card1, text="San Francisco", font=("Segoe UI", 16, "bold"), bg=CARD_BG, fg=TEXT_DARK)
title.pack()

# Gauge Canvas
g = Canvas(card1, width=300, height=150, bg=CARD_BG, highlightthickness=0)
g.pack(pady=5)

# Draw arc
g.create_arc(10, 10, 290, 290, start=180, extent=36, width=20, outline=GREEN, style="arc")
g.create_arc(10, 10, 290, 290, start=216, extent=36, width=20, outline=YELLOW, style="arc")
g.create_arc(10, 10, 290, 290, start=252, extent=36, width=20, outline=ORANGE, style="arc")
g.create_arc(10, 10, 290, 290, start=288, extent=36, width=20, outline=RED, style="arc")

# Needle
g.create_line(150, 150, 80, 120, width=4, fill=GREEN)

aqi_value = tk.Label(card1, text="42", font=("Segoe UI", 28, "bold"), bg=CARD_BG, fg=GREEN)
aqi_value.pack()

aqi_status = tk.Label(card1, text="Good", font=("Segoe UI", 14), bg=CARD_BG, fg=GREEN)
aqi_status.pack()

# ---------------------------------------------
# CARD 2: POLLUTANTS
# ---------------------------------------------
card2 = create_card(seconframe, 0, 1, 700, 250)

title = tk.Label(card2, text="Pollutant Levels", font=("Segoe UI", 14, "bold"), bg=CARD_BG, fg=TEXT_DARK)
title.pack()

def pollutant_row(parent, name, value, color):
    frame = tk.Frame(parent, bg=CARD_BG)
    frame.pack(fill="x", padx=10, pady=5)
    tk.Label(frame, text=name, bg=CARD_BG, fg=TEXT_DARK).pack(side="left")
    tk.Label(frame, text=f"{value} µg/m³", bg=CARD_BG, fg=TEXT_LIGHT).pack(side="right")

    canvas = Canvas(parent, width=250, height=8, bg=BAR_GRAY, highlightthickness=2)
    canvas.pack()
    
    canvas.create_rectangle(0, 0, value * 2, 8, fill=color, outline="")

pollutant_row(card2, "PM2.5", 12, GREEN) #WE can change 12 and tthe other numbers into the formula so it is responsive
pollutant_row(card2, "PM10", 25, YELLOW)
pollutant_row(card2, "O₃", 45, ORANGE)

# ---------------------------------------------
# MID CARDS (Locations)
# ---------------------------------------------
locations = [
    ("Downtown", 56, "Moderate", YELLOW),
    ("Airport", 38, "Good", GREEN),
    ("Industrial", 124, "Unhealthy", ORANGE),
    ("Coastal", 28, "Good", GREEN),
]

row =2
col = 0

for name, val, status, color in locations:
     
    # Create ONE card per location
    card = create_card(seconframe, row, col, 250, 120)
    
    tk.Label(card, text=name, bg=CARD_BG, fg=TEXT_DARK,
             font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    tk.Label(card, text=str(val), bg=CARD_BG, fg=color,
             font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=10)

    tk.Label(card, text=status, bg=CARD_BG, fg=color,
             font=("Segoe UI", 12)).pack(anchor="w", padx=10)

    # Move to next column
    col += 10
    
    # If column reaches 3, go to next row
    if col >= 4:
        col = 0
        row += 1

# ---------------------------------------------
# BOTTOM ROW: STATIC CHARTS
# ---------------------------------------------
# Chart 1: 24-hour Trend
chart_card = create_card(seconframe, 550, 300)
tk.Label(chart_card, text="24-Hour Trend", font=("Segoe UI", 14, "bold"), bg=CARD_BG, fg=TEXT_DARK).pack(anchor="w", padx=10)

fig, ax = plt.subplots(figsize=(5, 2.5))
ax.plot([40, 38, 39, 55, 60, 58, 45], linewidth=3)
ax.set_ylim(0, 80)
ax.set_xlabel("Time")
ax.set_ylabel("AQI")
fig.tight_layout()

canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(fig, master=chart_card)
canvas.get_tk_widget().pack()

# Chart 2: Bar Chart
chart_card2 = create_card(seconframe, 550, 300)
tk.Label(chart_card2, text="City Comparison", font=("Segoe UI", 14, "bold"), bg=CARD_BG, fg=TEXT_DARK).pack(anchor="w", padx=10)

fig2, ax2 = plt.subplots(figsize=(5, 2.5))
cities = ["SF", "LA", "NY", "Seattle"]
pm25 = [15, 30, 20, 10]
pm10 = [20, 50, 30, 18]

ax2.bar(cities, pm25, label="PM2.5")
ax2.bar(cities, pm10, bottom=pm25, label="PM10")
ax2.legend()
fig2.tight_layout()

canvas2 = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(fig2, master=chart_card2)
canvas2.get_tk_widget().pack()

# ---------------------------------------------
root.mainloop()
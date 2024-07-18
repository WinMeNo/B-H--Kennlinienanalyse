import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.interpolate import interp1d
from scipy.optimize import brentq

def load_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        process_file(file_path)

def find_intersection(H_upper_interp, H_lower_interp, B_diff):
    H_values = np.linspace(0, min(H_upper_interp.x[-1], H_lower_interp.x[-1]), 10000)
    intersections = []

    for i in range(len(H_values) - 1):
        if B_diff(H_values[i]) * B_diff(H_values[i + 1]) < 0:
            H_intersection = brentq(B_diff, H_values[i], H_values[i + 1])
            intersections.append(H_intersection)

    return intersections

def find_zero_crossing(interp_func, H_range):
    for i in range(len(H_range) - 1):
        if interp_func(H_range[i]) * interp_func(H_range[i + 1]) < 0:
            return brentq(interp_func, H_range[i], H_range[i + 1])
    return None

def process_file(file_path):
    global total_area
    data = pd.read_csv(file_path)
    H_upper = data.iloc[:, 2]
    B_upper = data.iloc[:, 3]
    H_lower = data.iloc[:, 4]
    B_lower = data.iloc[:, 5]

    # Lineare Interpolation innerhalb der Datenbereiche
    H_upper_interp = interp1d(H_upper, B_upper, kind='linear', fill_value="extrapolate")
    H_lower_interp = interp1d(H_lower, B_lower, kind='linear', fill_value="extrapolate")
    B_diff = lambda H: H_upper_interp(H) - H_lower_interp(H)

    # Find intersections
    intersections = find_intersection(H_upper_interp, H_lower_interp, B_diff)
    
    upper_zero_crossing = find_zero_crossing(H_upper_interp, np.linspace(H_upper.min(), H_upper.max(), 10000))
    lower_zero_crossing = find_zero_crossing(H_lower_interp, np.linspace(H_lower.min(), H_lower.max(), 10000))
    
    if upper_zero_crossing is not None:
        print(f"Die obere Hysteresekurve schneidet die H-Achse bei H = {upper_zero_crossing}")
    else:
        print("Die obere Hysteresekurve schneidet die H-Achse nicht.")

    if lower_zero_crossing is not None:
        print(f"Die untere Hysteresekurve schneidet die H-Achse bei H = {lower_zero_crossing}")
    else:
        print("Die untere Hysteresekurve schneidet die H-Achse nicht.")

    if intersections:
        for H in intersections:
            print(f"Ja, es gibt einen Schnittpunkt bei H = {H}")
        upper_limit = intersections[0]
    else:
        print("Nein, es gibt keinen Schnittpunkt")
        if H_upper.iloc[-1] < H_lower.iloc[-1]:
            print(f"Obere Hysteresekurve ist etwas kürzer. Der letzte H Wert liegt bei H = {H_upper.iloc[-1]}")
            upper_limit = H_upper.iloc[-1]
        elif H_lower.iloc[-1] < H_upper.iloc[-1]:
            print(f"Untere Hysteresekurve ist etwas kürzer. Der letzte H Wert liegt bei H = {H_lower.iloc[-1]}")
            upper_limit = H_lower.iloc[-1]
        else:
            print(f"Die Kurven sind gleich lang. Der letzte H Wert beider Kurven liegt bei H = {H_upper.iloc[-1]}")
            upper_limit = H_upper.iloc[-1]

    # Calculate the area under the upper hysteresis curve using the trapezoidal rule
    if upper_zero_crossing is not None:
        H_values_for_area_upper = np.linspace(upper_zero_crossing, upper_limit, 10000)
        B_values_for_area_upper = H_upper_interp(H_values_for_area_upper)
        area_upper = np.trapz(B_values_for_area_upper, H_values_for_area_upper)
        print(f"Fläche unter der oberen Hysteresekurve liegt bei {area_upper}")
    else:
        print("Keine Fläche unter der oberen Hysteresekurve berechnet.")

    # Calculate the area under the lower hysteresis curve using the trapezoidal rule
    if lower_zero_crossing is not None:
        H_values_for_area_lower = np.linspace(lower_zero_crossing, upper_limit, 10000)
        B_values_for_area_lower = H_lower_interp(H_values_for_area_lower)
        area_lower = np.trapz(B_values_for_area_lower, H_values_for_area_lower)
        print(f"Fläche unter der unteren Hysteresekurve liegt bei {area_lower}")
    else:
        print("Keine Fläche unter der unteren Hysteresekurve berechnet.")

    # Calculate the difference, double it, and display the result
    if 'area_upper' in locals() and 'area_lower' in locals():
        area_difference = abs(area_upper - area_lower)
        total_area = 2 * area_difference
        result_label.config(text=f"Gesamtfläche zwischen beiden Kurven: {total_area:.2f} Ws/m³")
        print(f"Gesamtfläche zwischen beiden Kurven liegt bei {total_area} Ws/m³")
        # Activate the input fields
        duration_entry.config(state='normal')
        density_entry.config(state='normal')
    else:
        total_area = None
        result_label.config(text="Gesamtfläche konnte nicht berechnet werden.")
        print("Gesamtfläche konnte nicht berechnet werden.")

    # Plot the data
    fig, ax = plt.subplots()
    H_range_upper = np.linspace(H_upper.min(), H_upper.max(), 10000)
    H_range_lower = np.linspace(H_lower.min(), H_lower.max(), 10000)
    
    # Plot original data
    ax.plot(H_upper, B_upper, 'o', label='Original Obere Hysteresekurve')
    ax.plot(H_lower, B_lower, 'o', label='Original Untere Hysteresekurve')
    
    # Plot interpolated data
    ax.plot(H_range_upper, H_upper_interp(H_range_upper), '-', label='Interpoliert Obere Hysteresekurve')
    ax.plot(H_range_lower, H_lower_interp(H_range_lower), '-', label='Interpoliert Untere Hysteresekurve')
    
    # Schraffierte Fläche obere Hysteresekurve
    if upper_zero_crossing is not None:
        ax.fill_between(H_values_for_area_upper, B_values_for_area_upper, alpha=0.3, color='blue', hatch='//')

    # Schraffierte Fläche untere Hysteresekurve
    if lower_zero_crossing is not None:
        ax.fill_between(H_values_for_area_lower, B_values_for_area_lower, alpha=0.3, color='red', hatch='\\')

    ax.legend(fontsize=11)
    ax.set_xlabel('H [A/m]', fontsize=13)
    ax.set_ylabel('B [T]', fontsize=13)
    ax.set_title('Ummagnetisierungsverluste', fontsize=13)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.grid(color='gray', linestyle='--', linewidth=0.5)
    ax.tick_params(axis='both', which='major', labelsize=13)

    # Display plot in Tkinter window
    for widget in plot_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Add the toolbar
    toolbar = NavigationToolbar2Tk(canvas, plot_frame)
    toolbar.update()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def calculate_loss_factor():
    global total_area
    try:
        duration = float(duration_entry.get())
        density = float(density_entry.get())
        if total_area is not None:
            loss_factor = total_area / (0.8 * duration * density)
            frequency = 1 / (0.8 * duration)
            loss_factor_label.config(text=f"Verlustkennzahl: {loss_factor:.2f} W/kg bei {frequency:.2f} Hz", font=('Helvetica', 13))
            # Hochrechnen der Verlustkennzahl auf 50 Hz
            loss_factor_50Hz = loss_factor * 50 * 0.8 * duration
            loss_factor_50Hz_label.config(text=f"Verlustkennzahl: {loss_factor_50Hz:.2f} W/kg bei 50 Hz", font=('Helvetica', 13))
        else:
            loss_factor_label.config(text="Berechnen Sie zuerst die Gesamtfläche.", font=('Helvetica', 13))
    except ValueError:
        messagebox.showerror("Eingabefehler", "Bitte geben Sie gültige Zahlen für die Messdauer und die Dichte ein.")

root = tk.Tk()
root.title("CSV File Loader")
root.geometry("800x600")

btn = tk.Button(root, text="Datei auswählen", command=load_file, font=('Helvetica', 13))
btn.pack(pady=20)

plot_frame = tk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=True)

result_label = tk.Label(root, text="", font=('Helvetica', 13))
result_label.pack(pady=10)

# Eingabefelder für Messdauer und Dichte, initial ausgegraut
input_frame = tk.Frame(root)
input_frame.pack(pady=5)

duration_label = tk.Label(input_frame, text="Messdauer in s:", font=('Helvetica', 13))
duration_label.grid(row=0, column=0, padx=5)

duration_entry = tk.Entry(input_frame, state='disabled', font=('Helvetica', 13))
duration_entry.grid(row=0, column=1, padx=5)

density_label = tk.Label(input_frame, text="Dichte in kg/m³:", font=('Helvetica', 13))
density_label.grid(row=0, column=2, padx=5)

density_entry = tk.Entry(input_frame, state='disabled', font=('Helvetica', 13))
density_entry.grid(row=0, column=3, padx=5)

calculate_button = tk.Button(input_frame, text="Verlustkennzahl berechnen", command=calculate_loss_factor, font=('Helvetica', 13))
calculate_button.grid(row=0, column=4, padx=5)

loss_factor_label = tk.Label(root, text="", font=('Helvetica', 13))
loss_factor_label.pack(pady=10)

loss_factor_50Hz_label = tk.Label(root, text="", font=('Helvetica', 13))
loss_factor_50Hz_label.pack(pady=10)

root.mainloop()

import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.interpolate import CubicSpline, interp1d

def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path)
        if len(df.columns) >= 6:
            original_data['H_neu'] = df.iloc[:, 0].values
            original_data['B_neu'] = df.iloc[:, 1].values
            original_data['H_oben'] = df.iloc[:, 2].values
            original_data['B_oben'] = df.iloc[:, 3].values
            original_data['H_unten'] = df.iloc[:, 4].values
            original_data['B_unten'] = df.iloc[:, 5].values
            update_plot()
        else:
            messagebox.showerror("Datei Fehler", "Die ausgewählte Datei hat nicht genügend Spalten.")
    else:
        messagebox.showerror("Datei Fehler", "Keine Datei ausgewählt.")

def modify_data():
    try:
        num_points_neu = int(neu_points_entry.get())
        num_points_oben = int(oben_points_entry.get())
        num_points_unten = int(unten_points_entry.get())
    except ValueError:
        messagebox.showerror("Eingabefehler", "Bitte gültige Zahlen für die Anzahl der Datenpunkte eingeben.")
        return

    def generate_points(H, B, num_points, method):
        sorted_indices = np.argsort(H)
        H_sorted = np.array(H)[sorted_indices]
        B_sorted = np.array(B)[sorted_indices]
        if method == 'cubic':
            interpolator = CubicSpline(H_sorted, B_sorted)
        elif method == 'quadratic':
            interpolator = interp1d(H_sorted, B_sorted, kind='quadratic')
        H_new = np.linspace(H_sorted.min(), H_sorted.max(), num_points)
        B_new = interpolator(H_new)
        return H_new, B_new

    try:
        modified_data['H_neu_cubic'], modified_data['B_neu_cubic'] = generate_points(original_data['H_neu'], original_data['B_neu'], num_points_neu, 'cubic')
        modified_data['H_oben_cubic'], modified_data['B_oben_cubic'] = generate_points(original_data['H_oben'], original_data['B_oben'], num_points_oben, 'cubic')
        modified_data['H_unten_cubic'], modified_data['B_unten_cubic'] = generate_points(original_data['H_unten'], original_data['B_unten'], num_points_unten, 'cubic')
        
        modified_data['H_neu_quad'], modified_data['B_neu_quad'] = generate_points(original_data['H_neu'], original_data['B_neu'], num_points_neu, 'quadratic')
        modified_data['H_oben_quad'], modified_data['B_oben_quad'] = generate_points(original_data['H_oben'], original_data['B_oben'], num_points_oben, 'quadratic')
        modified_data['H_unten_quad'], modified_data['B_unten_quad'] = generate_points(original_data['H_unten'], original_data['B_unten'], num_points_unten, 'quadratic')
    except KeyError as e:
        messagebox.showerror("Datenfehler", f"Fehlende Originaldaten: {str(e)}")
        return
    
    save_modified_data()
    update_plot()
    calculate_differences()

def save_modified_data():
    mod_df_cubic = pd.DataFrame({
        'H_neu_cubic': modified_data['H_neu_cubic'],
        'B_neu_cubic': modified_data['B_neu_cubic'],
        'H_oben_cubic': modified_data['H_oben_cubic'],
        'B_oben_cubic': modified_data['B_oben_cubic'],
        'H_unten_cubic': modified_data['H_unten_cubic'],
        'B_unten_cubic': modified_data['B_unten_cubic']
    })
    mod_df_cubic.to_csv('modified_data_cubic.csv', index=False)

    mod_df_quad = pd.DataFrame({
        'H_neu_quad': modified_data['H_neu_quad'],
        'B_neu_quad': modified_data['B_neu_quad'],
        'H_oben_quad': modified_data['H_oben_quad'],
        'B_oben_quad': modified_data['B_oben_quad'],
        'H_unten_quad': modified_data['H_unten_quad'],
        'B_unten_quad': modified_data['B_unten_quad']
    })
    mod_df_quad.to_csv('modified_data_quad.csv', index=False)

def calculate_differences():
    differences = {
        'Neukurve (kubisch)': np.abs(original_data['B_neu'] - CubicSpline(modified_data['H_neu_cubic'], modified_data['B_neu_cubic'])(original_data['H_neu'])),
        'Obere Hysterese (kubisch)': np.abs(original_data['B_oben'] - CubicSpline(modified_data['H_oben_cubic'], modified_data['B_oben_cubic'])(original_data['H_oben'])),
        'Untere Hysterese (kubisch)': np.abs(original_data['B_unten'] - CubicSpline(modified_data['H_unten_cubic'], modified_data['B_unten_cubic'])(original_data['H_unten'])),
        'Neukurve (quadratisch)': np.abs(original_data['B_neu'] - interp1d(modified_data['H_neu_quad'], modified_data['B_neu_quad'], kind='quadratic')(original_data['H_neu'])),
        'Obere Hysterese (quadratisch)': np.abs(original_data['B_oben'] - interp1d(modified_data['H_oben_quad'], modified_data['B_oben_quad'], kind='quadratic')(original_data['H_oben'])),
        'Untere Hysterese (quadratisch)': np.abs(original_data['B_unten'] - interp1d(modified_data['H_unten_quad'], modified_data['B_unten_quad'], kind='quadratic')(original_data['H_unten']))
    }
    for key, value in differences.items():
        print(f"Maximale Differenz für {key}: {np.max(value)}")

def update_plot():
    ax.clear()
    ax.grid(True)
    ax.set_xlabel('H [A/m]', fontsize=13)
    ax.set_ylabel('B [T]', fontsize=13)
    ax.set_title('B(H)-Kennlinie Modifikation', fontsize=13)
    
    if show_original_var.get():
        ax.plot(original_data['H_neu'], original_data['B_neu'], 'bo-', label='Original Neukurve')
        ax.plot(original_data['H_oben'], original_data['B_oben'], 'go-', label='Original obere Hysterese')
        ax.plot(original_data['H_unten'], original_data['B_unten'], 'ro-', label='Original untere Hysterese')

    if 'H_neu_cubic' in modified_data and show_cubic_var.get():
        ax.plot(modified_data['H_neu_cubic'], modified_data['B_neu_cubic'], 'bx', label='Modifiziert Neukurve (kubisch)', linestyle='None')
        ax.plot(modified_data['H_oben_cubic'], modified_data['B_oben_cubic'], 'gx', label='Modifiziert obere Hysterese (kubisch)', linestyle='None')
        ax.plot(modified_data['H_unten_cubic'], modified_data['B_unten_cubic'], 'rx', label='Modifiziert untere Hysterese (kubisch)', linestyle='None')
        for curve, label in zip(['H_neu_cubic', 'H_oben_cubic', 'H_unten_cubic'], ['Neukurve (kubisch)', 'obere Hysterese (kubisch)', 'untere Hysterese (kubisch)']):
            H = modified_data[curve]
            B = modified_data[f'B_{curve.split("_")[1]}_cubic']
            cs = CubicSpline(H, B)
            H_smooth = np.linspace(H.min(), H.max(), 500)
            B_smooth = cs(H_smooth)
            ax.plot(H_smooth, B_smooth, label=f'Modifiziert {label}', alpha=0.5)
    
    if 'H_neu_quad' in modified_data and show_quadratic_var.get():
        ax.plot(modified_data['H_neu_quad'], modified_data['B_neu_quad'], 'b+', label='Modifiziert Neukurve (quadratisch)', linestyle='None')
        ax.plot(modified_data['H_oben_quad'], modified_data['B_oben_quad'], 'g+', label='Modifiziert obere Hysterese (quadratisch)', linestyle='None')
        ax.plot(modified_data['H_unten_quad'], modified_data['B_unten_quad'], 'r+', label='Modifiziert untere Hysterese (quadratisch)', linestyle='None')
        for curve, label in zip(['H_neu_quad', 'H_oben_quad', 'H_unten_quad'], ['Neukurve (quadratisch)', 'obere Hysterese (quadratisch)', 'untere Hysterese (quadratisch)']):
            H = modified_data[curve]
            B = modified_data[f'B_{curve.split("_")[1]}_quad']
            qs = interp1d(H, B, kind='quadratic')
            H_smooth = np.linspace(H.min(), H.max(), 500)
            B_smooth_qs = qs(H_smooth)
            ax.plot(H_smooth, B_smooth_qs, label=f'Modifiziert {label}', alpha=0.5, linestyle='dashed')
    
    ax.legend(fontsize=11)
    canvas.draw()

root = tk.Tk()
root.title("CSV File Modifier")

original_data = {}
modified_data = {}

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

tk.Button(frame, text="Datei laden", command=load_file, font=('Helvetica', 13)).grid(row=0, column=0, padx=5, pady=5)

tk.Label(frame, text="Anzahl Datenpunkte Neukurve:", font=('Helvetica', 13)).grid(row=1, column=0, padx=5, pady=5)
neu_points_entry = tk.Entry(frame, font=('Helvetica', 13))
neu_points_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="Anzahl Datenpunkte obere Hysterese:", font=('Helvetica', 13)).grid(row=2, column=0, padx=5, pady=5)
oben_points_entry = tk.Entry(frame, font=('Helvetica', 13))
oben_points_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame, text="Anzahl Datenpunkte untere Hysterese:", font=('Helvetica', 13)).grid(row=3, column=0, padx=5, pady=5)
unten_points_entry = tk.Entry(frame, font=('Helvetica', 13))
unten_points_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Button(frame, text="Daten modifizieren", command=modify_data, font=('Helvetica', 13)).grid(row=4, column=0, columnspan=2, padx=5, pady=5)

show_original_var = tk.BooleanVar(value=True)
tk.Checkbutton(frame, text="Originaldaten anzeigen", variable=show_original_var, command=update_plot, font=('Helvetica', 13)).grid(row=5, column=0, columnspan=2, padx=5, pady=5)

show_cubic_var = tk.BooleanVar(value=True)
tk.Checkbutton(frame, text="Modifizierte Daten (kubisch) anzeigen", variable=show_cubic_var, command=update_plot, font=('Helvetica', 13)).grid(row=6, column=0, columnspan=2, padx=5, pady=5)

show_quadratic_var = tk.BooleanVar(value=True)
tk.Checkbutton(frame, text="Modifizierte Daten (quadratisch) anzeigen", variable=show_quadratic_var, command=update_plot, font=('Helvetica', 13)).grid(row=7, column=0, columnspan=2, padx=5, pady=5)

fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack()

root.mainloop()

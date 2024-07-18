import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.interpolate import interp1d
import tkinter as tk
from tkinter import filedialog, messagebox
import warnings

def load_and_process_data():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        messagebox.showerror("Dateiauswahl", "Keine Datei ausgewählt, Programm wird beendet.")
        root.quit()
        return

    # Einlesen der Daten
    dataframe = pd.read_csv(file_path)
    
    # Anzahl der Zeilen in der Datei
    num_rows = len(dataframe)
    
    # Berechnung der Anzahl der Punkte für die erste Interpolation 
    num_points_first_interp = max(10, num_rows // 2)               # Subsample: 2 heisst 50% der Datenpunkte, z.B.: 5 heisst 20% der Datenpunkte, 10 heisst 10% der Datenpunkte
                                                                   # Haben die Daten aktuell keine oder kaum Restwelligkeit kann Subsample von 1 gewählt werden (100% der Datenpunkte)
                                                                   # Ist die Restwelligkeit höher und man wünscht eine Minderung, dann Subsample-Wert > 1 wählen 
                                                                   # -> Ausprobieren bis gewünschtes Ergebnis erreicht wird. 
                                                                   
    # Initialisiere den neuen DataFrame für die interpolierten Daten
    global new_dataframe
    new_dataframe = pd.DataFrame()
    
    # Spalten für Interpolation definieren
    columns_to_process = [(2, 3), (6, 7), (10, 11)]
    
    all_data = []  # Zum Speichern der Daten für das Plotting
    
    for i, (H_col, B_col) in enumerate(columns_to_process, start=1):
        H_values = dataframe.iloc[:, H_col].values
        B_values = dataframe.iloc[:, B_col].values

        # Bereinigung von Duplikaten: Mittelwert von B für jeden eindeutigen H-Wert
        df_cleaned = pd.DataFrame({'H': H_values, 'B': B_values})
        df_cleaned = df_cleaned.groupby('H').mean().reset_index()

        # Sortierung der Daten
        H_sorted = df_cleaned['H'].values
        B_sorted = df_cleaned['B'].values

        # Erste kubische Interpolation
        cubic_interp1 = interp1d(H_sorted, B_sorted, kind='cubic', fill_value="extrapolate")

        # Erzeugen diskreter H-Werte und Berechnung der B-Werte
        H_new = np.linspace(min(H_sorted), max(H_sorted), num=num_points_first_interp)
        B_new = cubic_interp1(H_new)

        # Zweite kubische Interpolation über die neuen H- und B-Werte
        cubic_interp2 = interp1d(H_new, B_new, kind='cubic', fill_value="extrapolate")
        H_fine = np.linspace(min(H_new), max(H_new), num=num_rows)
        B_fine = cubic_interp2(H_fine)

        # Speichern der Daten im DataFrame für die zweite Interpolation
        new_dataframe[f'H_fine_{i}'] = H_fine
        new_dataframe[f'B_fine_{i}'] = B_fine

        # Speichern der Daten für das Plotting
        all_data.append((H_sorted, B_sorted, H_new, B_new, H_fine, B_fine, i))
    
    # Plotten aller Daten in einem einzigen Plot
    plot_all_data(all_data)

def plot_all_data(all_data):
    fig, ax = plt.subplots()
    colors = ['blue', 'red', 'green']  # Farben für Originaldaten, erste und zweite Interpolation
    lines = []

    for (H_sorted, B_sorted, H_new, B_new, H_fine, B_fine, index), color in zip(all_data, colors):
        line1, = ax.plot(H_sorted, B_sorted, 'x-', label=f'Gefilterte Daten {index}', color=colors[0])  # Linie mit x-Markern
        line2, = ax.plot(H_new, B_new, 'o-', label=f'Erste Interpolation {index}', color=colors[1], linestyle='-')  # Durchgezogene Linie
        line3, = ax.plot(H_fine, B_fine, 's-', label=f'Zweite Interpolation {index}', color=colors[2], linestyle='-')  # Durchgezogene Linie
        lines.append((line1, line2, line3))

    ax.set_xlabel('Feldstärke H (A/m)', fontsize=12)
    ax.set_ylabel('Flussdichte B (T)', fontsize=12)
    ax.set_title('Vergleich von Original und interpolierten Daten', fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True)
    ax.tick_params(axis='both', which='major', labelsize=12)

    def toggle_lines():
        for i, (line1, line2, line3) in enumerate(lines):
            line1.set_visible(var1.get())
            line2.set_visible(var2.get())
            line3.set_visible(var3.get())
        canvas.draw()

    var1 = tk.BooleanVar(value=True)
    var2 = tk.BooleanVar(value=True)
    var3 = tk.BooleanVar(value=True)

    check1 = tk.Checkbutton(root, text="Originaldaten", variable=var1, command=toggle_lines, font=('Helvetica', 11))
    check2 = tk.Checkbutton(root, text="Erste Interpolation", variable=var2, command=toggle_lines, font=('Helvetica', 11))
    check3 = tk.Checkbutton(root, text="Zweite Interpolation", variable=var3, command=toggle_lines, font=('Helvetica', 11))
    
    check1.pack(side=tk.LEFT, padx=5)
    check2.pack(side=tk.LEFT, padx=5)
    check3.pack(side=tk.LEFT, padx=5)

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    save_button = tk.Button(root, text="Daten speichern", command=save_data, font=('Helvetica', 12))
    save_button.pack(side=tk.BOTTOM, pady=10)

def save_data():
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Speichern der interpolierten Daten")
    if save_path:
        new_dataframe.to_csv(save_path, index=False)
        print("Interpolierte Daten wurden gespeichert.")
        print(new_dataframe.tail(50))  # Anzeige der letzten 50 Datenpunkte

# Warnungen deaktivieren
warnings.filterwarnings("ignore", category=UserWarning)

root = tk.Tk()
root.title("Interaktive Hystereseschleife Anzeige")
load_button = tk.Button(root, text="Daten laden und verarbeiten", command=load_and_process_data, font=('Helvetica', 12))
load_button.pack(side=tk.BOTTOM, pady=10)
root.mainloop()

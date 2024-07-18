import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tkinter import Tk, filedialog, Button
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import CheckButtons
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# Konstante für die magnetische Feldkonstante μ0
mu_0 = 4 * np.pi * 10**-7

# Funktion zur Berechnung der Magnetisierung
def magnetization(B, H):
    return B / mu_0 - H

# Funktion zur Berechnung der Polarisation
def polarization(B, H):
    return B - mu_0 * H

# Funktion zur Verarbeitung der ausgewählten Datei
def process_file(file_path):
    if not file_path:
        print("Keine Datei ausgewählt. Das Programm wird beendet.")
        return
    data = pd.read_csv(file_path)
    print("Rohdaten:")
    print(data.head())  # Debugging-Ausgabe: Zeige die ersten Zeilen der Rohdaten
    
    result_data_magnetization = []
    result_data_polarization = []
    
    # Berechnung der Magnetisierung und Polarisation für obere Hystereseschleife
    for index, row in data.iterrows():
        H_upper = float(row['H_fine_2'])
        B_upper = float(row['B_fine_2'])
        M_upper = magnetization(B_upper, H_upper)
        J_upper = polarization(B_upper, H_upper)
        result_data_magnetization.append({'H_upper': H_upper, 'M_upper': M_upper})
        result_data_polarization.append({'H_upper': H_upper, 'J_upper': J_upper})
        
    # Berechnung der Magnetisierung und Polarisation für untere Hystereseschleife
    for index, row in data.iterrows():
        H_lower = float(row['H_fine_3'])
        B_lower = float(row['B_fine_3'])
        M_lower = magnetization(B_lower, H_lower)
        J_lower = polarization(B_lower, H_lower)
        result_data_magnetization.append({'H_lower': H_lower, 'M_lower': M_lower})
        result_data_polarization.append({'H_lower': H_lower, 'J_lower': J_lower})
    
    result_df_magnetization = pd.DataFrame(result_data_magnetization)
    result_df_polarization = pd.DataFrame(result_data_polarization)
    
    result_df_magnetization.to_csv('berechnete_magnetisierung.csv', index=False)
    result_df_polarization.to_csv('berechnete_polarisation.csv', index=False)
    
    # Erstelle ein Tkinter-Fenster und bette den Matplotlib-Plot darin ein
    plot_window = Tk()
    plot_window.title("Interaktiver Plot")

    # Erstelle die Figur und die beiden Achsen
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    plt.subplots_adjust(left=0.3, hspace=0.5)  # Platz für die Checkbuttons lassen und Abstand zwischen den Plots

    # Erster Plot: Magnetisierungsdaten
    l1, = ax1.plot(result_df_magnetization['H_upper'], result_df_magnetization['M_upper'], label='Magnetisierung oben', color='blue')
    l2, = ax1.plot(result_df_magnetization['H_lower'], result_df_magnetization['M_lower'], label='Magnetisierung unten', color='cyan')
    ax1.set_xlabel('H [A/m]', fontsize=13)
    ax1.set_ylabel('M [A/m]', fontsize=13)
    ax1.set_title('Magnetisierung', fontsize=13)
    ax1.grid(True)
    ax1.legend(loc='upper right', fontsize=11)
    ax1.tick_params(axis='both', which='major', labelsize=13)

    # Zweiter Plot: Polarisationsdaten
    l3, = ax2.plot(result_df_polarization['H_upper'], result_df_polarization['J_upper'], label='Polarisation oben', color='green')
    l4, = ax2.plot(result_df_polarization['H_lower'], result_df_polarization['J_lower'], label='Polarisation unten', color='lightgreen')
    ax2.set_xlabel('H [A/m]', fontsize=13)
    ax2.set_ylabel('J [T]', fontsize=13)
    ax2.set_title('Polarisation', fontsize=13)
    ax2.grid(True)
    ax2.legend(loc='upper right', fontsize=11)
    ax2.tick_params(axis='both', which='major', labelsize=13)

    # Checkbuttons erstellen
    rax = plt.axes([0.05, 0.4, 0.2, 0.2])
    labels = ['Magnetisierung oben', 'Magnetisierung unten', 'Polarisation oben', 'Polarisation unten']
    visibility = [True, True, True, True]
    check = CheckButtons(rax, labels, visibility)

    # Funktion zum Ein- und Ausblenden der Linien
    def func(label):
        if label == 'Magnetisierung oben':
            l1.set_visible(not l1.get_visible())
        elif label == 'Magnetisierung unten':
            l2.set_visible(not l2.get_visible())
        elif label == 'Polarisation oben':
            l3.set_visible(not l3.get_visible())
        elif label == 'Polarisation unten':
            l4.set_visible(not l4.get_visible())
        plt.draw()

    check.on_clicked(func)

    # Canvas erstellen und Matplotlib-Figur einbetten
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

    # Navigationstoolbar hinzufügen (für Zoom- und Schwenk-Funktionalität)
    toolbar = NavigationToolbar2Tk(canvas, plot_window)
    toolbar.update()
    canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

    plot_window.mainloop()

# Funktion zum Öffnen des Dateiauswahldialogs
def open_file_dialog():
    root = Tk()
    root.withdraw()  # Verhindert das Anzeigen des leeren Fensters
    file_path = filedialog.askopenfilename()  # Öffnet den Dateiauswahldialog
    root.destroy()  # Schließt das Tkinter-Fenster
    process_file(file_path)

# Den Tkinter-Hauptloop starten
root = Tk()
root.geometry("200x50")  # Setze die Größe des Fensters
button = Button(root, text="Durchsuchen", command=open_file_dialog, font=('Helvetica', 13))
button.pack()

root.mainloop()

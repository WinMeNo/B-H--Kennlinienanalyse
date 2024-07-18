import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tkinter import Tk, filedialog, Button
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import CheckButtons
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from scipy.signal import savgol_filter
from scipy.interpolate import CubicSpline

# Konstante für die magnetische Feldkonstante μ0
mu_0 = 4 * np.pi * 10**-7

# Funktion zur Berechnung der relativen Permeabilität durch Steigungsberechnung
def relative_permeability(H, B):
    # Glättung der Daten
    B_smooth = savgol_filter(B, window_length=11, polyorder=3)
    H_smooth = savgol_filter(H, window_length=11, polyorder=3)
    
    # Berechnung der Steigung mittels zentraler Differenzenmethode auf den geglätteten Daten
    dB_dH = np.gradient(B_smooth, H_smooth)
    
    return dB_dH / mu_0

# Funktion zur Verarbeitung der ausgewählten Datei
def process_file(file_path):
    if not file_path:
        print("Keine Datei ausgewählt. Das Programm wird beendet.")
        return
    data = pd.read_csv(file_path)
    print("Rohdaten:")
    print(data.head())  # Debugging-Ausgabe: Zeige die ersten Zeilen der Rohdaten
    
    result_data = []
    
    # Subsampling der Daten zur Reduzierung der Auflösung
    subsample_factor = 10  # Faktor zur Reduzierung der Auflösung, hier kannst du den Wert ändern (über jeden x-ten Datenpunkt werden die Permeabilitäten berechnet || hier: über jeden 10ten Datenpunkt)
    H = data['H_fine_1'].values
    B = data['B_fine_1'].values
    H_subsampled = H[::subsample_factor]
    B_subsampled = B[::subsample_factor]
    
    # Berechne die Permeabilität durch Steigungsberechnung
    mu = relative_permeability(H_subsampled, B_subsampled)
    
    for h, b, m in zip(H_subsampled, B_subsampled, mu):
        result_data.append({'Original_H': h, 'Original_B': b, 'mu': m})
    
    result_df = pd.DataFrame(result_data)
    result_df.to_csv('berechnete_permeabilitaeten.csv', index=False)
    
    # Erstelle ein Tkinter-Fenster und bette den Matplotlib-Plot darin ein
    plot_window = Tk()
    plot_window.title("Interaktiver Plot")

    # Erstelle die Figur und die beiden Achsen
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    plt.subplots_adjust(left=0.3, hspace=0.5)  # Platz für die Checkbuttons lassen und Abstand zwischen den Plots

    # Cubic Spline Interpolation der Datenpunkte
    cs1 = CubicSpline(result_df['Original_H'], result_df['Original_B'])
    cs2 = CubicSpline(result_df['Original_H'], result_df['mu'])
    
    # Erster Plot: Original H-B Daten
    ax1.plot(result_df['Original_H'], result_df['Original_B'], 'o', label='Originaldaten H-B', color='blue')
    ax1.plot(result_df['Original_H'], cs1(result_df['Original_H']), label='Interpolierte H-B Kurve', color='blue')
    ax1.set_xlabel('H [A/m]', fontsize=13)
    ax1.set_ylabel('B [T]', fontsize=13)
    ax1.set_title('Originaldaten H-B', fontsize=13)
    ax1.grid(True)
    ax1.legend(loc='upper right', fontsize=11)
    ax1.tick_params(axis='both', which='major', labelsize=13)

    # Zweiter Plot: Berechnete Permeabilitäten
    ax2.plot(result_df['Original_H'], result_df['mu'], 'o', label='Berechnete Permeabilitäten', color='green')
    ax2.plot(result_df['Original_H'], cs2(result_df['Original_H']), label='Interpolierte Permeabilitäten Kurve', color='green')
    ax2.set_xlabel('H [A/m]', fontsize=13)
    ax2.set_ylabel('μ [Vs/Am]', fontsize=13)
    ax2.set_title('Berechnete Permeabilitäten', fontsize=13)  # Korrigiert zu set_title
    ax2.grid(True)
    ax2.legend(loc='upper right', fontsize=11)
    ax2.tick_params(axis='both', which='major', labelsize=13)

    # Checkbuttons erstellen
    rax = plt.axes([0.05, 0.4, 0.2, 0.15])
    labels = ['Originaldaten H-B', 'Interpolierte H-B Kurve', 'Berechnete Permeabilitäten', 'Interpolierte Permeabilitäten Kurve']
    visibility = [True, True, True, True]
    check = CheckButtons(rax, labels, visibility)

    # Funktion zum Ein- und Ausblenden der Linien
    def func(label):
        if label == 'Originaldaten H-B':
            ax1.lines[0].set_visible(not ax1.lines[0].get_visible())
        elif label == 'Interpolierte H-B Kurve':
            ax1.lines[1].set_visible(not ax1.lines[1].get_visible())
        elif label == 'Berechnete Permeabilitäten':
            ax2.lines[0].set_visible(not ax2.lines[0].get_visible())
        elif label == 'Interpolierte Permeabilitäten Kurve':
            ax2.lines[1].set_visible(not ax2.lines[1].get_visible())
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

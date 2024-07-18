import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tkinter import Tk, filedialog, Button, Label
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import CheckButtons
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# Funktion zur Berechnung der Remanenz mit linearer Interpolation
def calculate_remanence(h_values, b_values):
    zero_crossing_index = np.where(np.diff(np.sign(h_values)))[0]

    if len(zero_crossing_index) == 0:
        return None  # Kein Schnittpunkt mit der Y-Achse gefunden

    zero_crossing_index = zero_crossing_index[0]

    # Werte vor und nach dem Schnittpunkt
    h1, h2 = h_values.iloc[zero_crossing_index], h_values.iloc[zero_crossing_index + 1]
    b1, b2 = b_values.iloc[zero_crossing_index], b_values.iloc[zero_crossing_index + 1]

    # Lineare Interpolation
    remanence = b1 + (b2 - b1) * (0 - h1) / (h2 - h1)
    
    return remanence

# Funktion zur Berechnung der Koerzitivfeldstärke mit linearer Interpolation
def calculate_coercivity(h_values, b_values):
    zero_crossing_index = np.where(np.diff(np.sign(b_values)))[0]

    if len(zero_crossing_index) == 0:
        return None  # Kein Schnittpunkt mit der X-Achse gefunden

    zero_crossing_index = zero_crossing_index[0]

    # Werte vor und nach dem Schnittpunkt
    b1, b2 = b_values.iloc[zero_crossing_index], b_values.iloc[zero_crossing_index + 1]
    h1, h2 = h_values.iloc[zero_crossing_index], h_values.iloc[zero_crossing_index + 1]

    # Lineare Interpolation
    coercivity = h1 + (h2 - h1) * (0 - b1) / (b2 - b1)
    
    return coercivity

# Funktion zur Verarbeitung der ausgewählten Datei
def process_file(file_path):
    if not file_path:
        print("Keine Datei ausgewählt. Das Programm wird beendet.")
        return
    data = pd.read_csv(file_path)
    print("Rohdaten:")
    print(data.head())  # Debugging-Ausgabe: Zeige die ersten Zeilen der Rohdaten

    # Berechne die obere Remanenz
    h_values_upper = data.iloc[:, 2]
    b_values_upper = data.iloc[:, 3]
    upper_remanence = calculate_remanence(h_values_upper, b_values_upper)

    if upper_remanence is None:
        print("Kein Schnittpunkt mit der Y-Achse für obere Remanenz gefunden.")
        upper_remanence = "Nicht gefunden"
    else:
        print(f"Obere Remanenz: {upper_remanence}")

    # Berechne die untere Remanenz
    h_values_lower = data.iloc[:, 4]
    b_values_lower = data.iloc[:, 5]
    lower_remanence = calculate_remanence(h_values_lower, b_values_lower)

    if lower_remanence is None:
        print("Kein Schnittpunkt mit der Y-Achse für untere Remanenz gefunden.")
        lower_remanence = "Nicht gefunden"
    else:
        print(f"Untere Remanenz: {lower_remanence}")

    # Berechne die negative Koerzitivfeldstärke (obere Hystereseschleife)
    negative_coercivity = calculate_coercivity(h_values_upper, b_values_upper)

    if negative_coercivity is None:
        print("Kein Schnittpunkt mit der X-Achse für negative Koerzitivfeldstärke gefunden.")
        negative_coercivity = "Nicht gefunden"
    else:
        print(f"Negative Koerzitivfeldstärke: {negative_coercivity}")

    # Berechne die positive Koerzitivfeldstärke (untere Hystereseschleife)
    positive_coercivity = calculate_coercivity(h_values_lower, b_values_lower)

    if positive_coercivity is None:
        print("Kein Schnittpunkt mit der X-Achse für positive Koerzitivfeldstärke gefunden.")
        positive_coercivity = "Nicht gefunden"
    else:
        print(f"Positive Koerzitivfeldstärke: {positive_coercivity}")

    # Erstelle ein Tkinter-Fenster und bette den Matplotlib-Plot darin ein
    plot_window = Tk()
    plot_window.title("Interaktiver Plot")

    # Erstelle die Figur und die Achsen
    fig, ax = plt.subplots(figsize=(10, 6))  # Größe der Figur erhöhen
    plt.subplots_adjust(left=0.3)  # Platz für die Checkbuttons lassen

    # Plotten der Daten
    l1, = ax.plot(data.iloc[:, 0], data.iloc[:, 1], label='H-B Schleife 1', color='blue')
    l2, = ax.plot(data.iloc[:, 2], data.iloc[:, 3], label='H-B Schleife 2', color='green')
    l3, = ax.plot(data.iloc[:, 4], data.iloc[:, 5], label='H-B Schleife 3', color='red')

    ax.set_xlabel('H [A/m]', fontsize=13)
    ax.set_ylabel('B [T]', fontsize=13)
    ax.set_title('Hystereseschleifen', fontsize=13)
    ax.grid(True)
    ax.legend(loc='upper right', fontsize=11)
    ax.tick_params(axis='both', which='major', labelsize=13)

    # Checkbuttons erstellen
    rax = plt.axes([0.05, 0.4, 0.2, 0.15])
    labels = ['H-B Schleife 1', 'H-B Schleife 2', 'H-B Schleife 3']
    visibility = [True, True, True]
    check = CheckButtons(rax, labels, visibility)

    # Funktion zum Ein- und Ausblenden der Linien
    def func(label):
        if label == 'H-B Schleife 1':
            l1.set_visible(not l1.get_visible())
        elif label == 'H-B Schleife 2':
            l2.set_visible(not l2.get_visible())
        elif label == 'H-B Schleife 3':
            l3.set_visible(not l3.get_visible())
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

    # Remanenz- und Koerzitivfeldstärkewerte unterhalb des Plots anzeigen
    label = Label(plot_window, text=f"Obere Remanenz: {upper_remanence} T \nUntere Remanenz: {lower_remanence} T\nNegative Koerzitivfeldstärke: {negative_coercivity} A/m\nPositive Koerzitivfeldstärke: {positive_coercivity} A/m", font=('Helvetica', 13))
    label.pack()

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

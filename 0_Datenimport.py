import pandas as pd
import matplotlib.pyplot as plt
import os
from tkinter import filedialog, messagebox
import tkinter as tk

# Setze die Anzeigeoptionen für alle DataFrames
pd.set_option('display.max_rows', None)  # Alle Zeilen anzeigen
pd.set_option('display.max_columns', None)  # Alle Spalten anzeigen
pd.set_option('display.width', 1000)  # Anzeigebreite für DataFrame festlegen
pd.set_option('display.float_format', lambda x: '{:.19f}'.format(x))  # Volle Genauigkeit für Fließkommazahlen

def interpolate_missing_values(df):
    # Interpoliert fehlende Werte linear und füllt verbleibende NaNs, die nicht interpoliert werden können,
    # erst von hinten (bfill) und dann von vorne (ffill).
    return df.interpolate().bfill().ffill()

def read_txt_file(file_path):
    data_lines = []
    data_started = False
    previous_line = None
    column_names_with_prefix = None
    column_names_without_prefix = None
    Kennlinienwerte = None

    with open(file_path, 'r') as file:
        for line in file:
            if data_started:
                data_lines.append(line.strip().split('\t'))
            elif 'Startkurve' in line:
                data_started = True
                if previous_line:
                    nk_prefix = 'NK_'
                    oh_prefix = 'OH_'
                    uh_prefix = 'UH_'
                    nk_words_with_prefix = [nk_prefix + word for word in previous_line[:2]]
                    oh_words_with_prefix = [oh_prefix + word for word in previous_line[2:4]]
                    uh_words_with_prefix = [uh_prefix + word for word in previous_line[4:]]
                    column_names_with_prefix = nk_words_with_prefix + oh_words_with_prefix + uh_words_with_prefix
                    column_names_without_prefix = previous_line[:2] + previous_line[2:4] + previous_line[4:]

                    if column_names_without_prefix[0] == 'FeldstÃ¤rke in A/m' and column_names_without_prefix[1] == 'Flussdichte in T':
                        Kennlinienwerte = 'B(H) - Kennlinie'
                    elif column_names_without_prefix[0] == 'Zeit in s' and column_names_without_prefix[1] == 'FeldstÃ¤rke in A/m':
                        Kennlinienwerte = 'H(t) - Kennlinie'
                    elif column_names_without_prefix[0] == 'Zeit in s' and column_names_without_prefix[1] == 'Strom in A':
                        Kennlinienwerte = 'I(t) - Kennlinie'
                    elif column_names_without_prefix[0] == 'Magnetische Spannung, A' and column_names_without_prefix[1] == 'Magnetischer Fluss, Vs':
                        Kennlinienwerte = 'Phi(Theta) - Kennlinie'
                    elif column_names_without_prefix[0] == 'Strom in A' and column_names_without_prefix[1] == 'Verketteter magnetischer Fluss in Vs':
                        Kennlinienwerte = 'Psi(i) - Kennlinie'
                    elif column_names_without_prefix[0] == 'Zeit in s' and column_names_without_prefix[1] == 'Spannung in V':
                        Kennlinienwerte = 'U(t) - Kennlinie'
                    else:
                        Kennlinienwerte = 'Unbekannt'
            previous_line = line.strip().split('\t')

    return data_lines, column_names_with_prefix, column_names_without_prefix, Kennlinienwerte

def process_file(file_path):
    dataset, column_names_with_prefix, column_names_without_prefix, Kennlinienwerte = read_txt_file(file_path)
    if dataset:
        df = pd.DataFrame(dataset, columns=column_names_with_prefix)
        df = df.apply(pd.to_numeric, errors='coerce')
        df = interpolate_missing_values(df)

        filename = f"{Kennlinienwerte.replace(' ', '_').replace('/', '_')}.csv"
        df.to_csv(filename, index=False)
        print(f"Dataframe als '{filename}' gespeichert.")

        if not df.empty:
            print("\nDie ersten 150 Zeilen des neuen DataFrames:")
            print(df.head(150))  # Zeigt nur die ersten 150 Zeilen an

            plt.figure(figsize=(10, 6))
            plt.plot(df[column_names_with_prefix[0]], df[column_names_with_prefix[1]], label="Neukurve", linestyle='-')
            plt.plot(df[column_names_with_prefix[2]], df[column_names_with_prefix[3]], label="Obere Grenzkurve", linestyle='-')
            plt.plot(df[column_names_with_prefix[4]], df[column_names_with_prefix[5]], label="Untere Grenzkurve", linestyle='-')
            plt.xlabel(column_names_without_prefix[0], fontsize=11)
            plt.ylabel(column_names_without_prefix[1], fontsize=11)
            plt.title(Kennlinienwerte, fontsize=12)
            plt.xticks(fontsize=11)
            plt.yticks(fontsize=11)
            plt.grid(True)
            plt.legend(fontsize=10)
            plt.show()
        else:
            print("Keine gültigen Daten zum Plotten vorhanden.")
    else:
        print("Datensatz nicht gefunden.")

def browse_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        process_file(file_path)
    else:
        print("Keine Datei ausgewählt.")

def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                print(f"Verarbeitung der Datei: {filename}")
                process_file(file_path)
    else:
        print("Kein Ordner ausgewählt.")

root = tk.Tk()
root.title("Datei- und Ordnerauswahl")
browse_file_button = tk.Button(root, text="Datei durchsuchen", command=browse_file)
browse_folder_button = tk.Button(root, text="Ordner durchsuchen", command=browse_folder)
browse_file_button.pack(pady=10)
browse_folder_button.pack(pady=10)
root.mainloop()

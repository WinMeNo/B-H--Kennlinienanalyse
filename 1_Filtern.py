import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import filedialog
from scipy.signal import butter, filtfilt

def calculate_errors(original, filtered):
    mae = np.mean(np.abs(original - filtered))
    mse = np.mean((original - filtered) ** 2)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((original - filtered) / (original + np.finfo(float).eps))) * 100
    mean_original = np.mean(original)
    rmse_percent = (rmse / abs(mean_original)) * 100
    return mae, mse, rmse, mape, rmse_percent

def calculate_snr(signal, noise):
    signal_power = np.mean(signal ** 2)
    noise_power = np.mean(noise ** 2)
    snr = 10 * np.log10(signal_power / noise_power)
    return snr

def load_and_process_data():
    global first_filtered_dataframe, final_dataframe, dataframe
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        print("Keine Datei ausgewählt, Programm wird beendet.")
        root.quit()
        return

    dataframe = pd.read_csv(file_path)
    print("Dataframe columns:", dataframe.columns)
    print("Dataframe shape:", dataframe.shape)

    # Erste Filterung
    apply_first_filter()

def apply_first_filter():
    global first_filtered_dataframe, final_dataframe
    filter_params_first = {
        0: {'order': 3, 'cutoff': 0.05},  # Erste Filterung Neukurve
        2: {'order': 3, 'cutoff': 0.05},  # Erste Filterung obere Hysterese
        4: {'order': 3, 'cutoff': 0.05}   # Erste Filterung untere Hysterese
    }

    columns_data_first = {}
    for i in range(0, 6, 2):
        order_first = filter_params_first[i]['order']
        cutoff_first = filter_params_first[i]['cutoff']
        b_first, a_first = butter(order_first, cutoff_first, btype='low', analog=False)
        original_h = dataframe.iloc[:, i].values
        original_b = dataframe.iloc[:, i + 1].values
        filtered_h = filtfilt(b_first, a_first, original_h)
        filtered_b = filtfilt(b_first, a_first, original_b)

        columns_data_first[f'H_original_{i//2}'] = original_h
        columns_data_first[f'B_original_{i//2}'] = original_b
        columns_data_first[f'H_filtered_{i//2}'] = filtered_h
        columns_data_first[f'B_filtered_{i//2}'] = filtered_b

    first_filtered_dataframe = pd.DataFrame(columns_data_first)
    first_output_filename = "first_filtered_data.csv"
    first_filtered_dataframe.to_csv(first_output_filename, index=False)
    print(f"Erste Filterung DataFrame wurde als '{first_output_filename}' gespeichert.")

    # Leeres DataFrame für die zweite Filterung erstellen
    final_dataframe = pd.DataFrame()

    update_plot()
    save_button['state'] = 'normal'
    filter_again_button['state'] = 'normal'

def apply_second_filter():
    global final_dataframe
    filter_params_second = {
        0: {'order': 4, 'cutoff': 0.01}, # Zweite Filterung Neukurve
        2: {'order': 4, 'cutoff': 0.01}, # Zweite Filterung obere Hysterese
        4: {'order': 4, 'cutoff': 0.01}  # Zweite Filterung untere Hysterese
    }

    columns_data_final = {}
    for i in range(0, 6, 2):
        order_second = filter_params_second[i]['order']
        cutoff_second = filter_params_second[i]['cutoff']
        b_second, a_second = butter(order_second, cutoff_second, btype='low', analog=False)
        filtered_h = first_filtered_dataframe[f'H_filtered_{i//2}'].values
        refiltered_h = filtfilt(b_second, a_second, filtered_h)
        filtered_b = first_filtered_dataframe[f'B_filtered_{i//2}'].values

        columns_data_final[f'H_original_{i//2}'] = first_filtered_dataframe[f'H_original_{i//2}'].values
        columns_data_final[f'B_original_{i//2}'] = first_filtered_dataframe[f'B_original_{i//2}'].values
        columns_data_final[f'H_refiltered_{i//2}'] = refiltered_h
        columns_data_final[f'B_filtered_{i//2}'] = filtered_b

    final_dataframe = pd.DataFrame(columns_data_final)
    final_output_filename = "final_filtered_data.csv"
    final_dataframe.to_csv(final_output_filename, index=False)
    print(f"Endgültig gefilterte DataFrame wurde als '{final_output_filename}' gespeichert.")

    update_plot()

def update_plot():
    ax.clear()
    for i in range(3):
        if show_original.get():
            ax.plot(first_filtered_dataframe[f'H_original_{i}'], first_filtered_dataframe[f'B_original_{i}'], label=f'Original {i + 1}')
        if show_filtered_h.get():
            ax.plot(first_filtered_dataframe[f'H_filtered_{i}'], first_filtered_dataframe[f'B_original_{i}'], label=f'H gefiltert {i + 1}')
        if show_filtered_b.get():
            ax.plot(first_filtered_dataframe[f'H_filtered_{i}'], first_filtered_dataframe[f'B_filtered_{i}'], label=f'H & B gefiltert {i + 1}')
        if show_refiltered.get() and not final_dataframe.empty:
            ax.plot(final_dataframe[f'H_refiltered_{i}'], final_dataframe[f'B_filtered_{i}'], label=f'H (2. Filterung) gefiltert {i + 1}')

    ax.set_xlabel('H [A/m]', fontsize=11)
    ax.set_ylabel('B [T]', fontsize=11)
    ax.set_title('Hystereseschleife', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True)
    ax.tick_params(axis='both', which='major', labelsize=11)
    canvas.draw()

def save_filtered_data():
    file_path_first = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Speichern der ersten Filterung")
    if file_path_first:
        first_filtered_dataframe.to_csv(file_path_first, index=False)
        print(f"Erste Filterung Daten wurden als '{file_path_first}' gespeichert.")

    file_path_final = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Speichern der endgültigen Filterung")
    if file_path_final:
        final_dataframe.to_csv(file_path_final, index=False)
        print(f"Endgültig gefilterte Daten wurden als '{file_path_final}' gespeichert.")

root = tk.Tk()
root.title("Original- und gefilterte Hystereseschleife")
fig = plt.Figure(figsize=(6, 4), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

results_text = tk.Text(root, height=10)
results_text.pack(side=tk.BOTTOM, fill=tk.X)
results_text.tag_configure('bold', font=('Helvetica', 12, 'bold'))

load_button = tk.Button(root, text="Daten laden", command=load_and_process_data)
load_button.pack(side=tk.LEFT, pady=10)

save_button = tk.Button(root, text="Daten speichern", command=save_filtered_data)
save_button.pack(side=tk.RIGHT, pady=10)

filter_again_button = tk.Button(root, text="Nochmals filtern", command=apply_second_filter)
filter_again_button.pack(side=tk.RIGHT, pady=10)
filter_again_button['state'] = 'disabled'

# Checkboxen hinzufügen
show_original = tk.BooleanVar(value=True)
show_filtered_h = tk.BooleanVar(value=True)
show_filtered_b = tk.BooleanVar(value=True)
show_refiltered = tk.BooleanVar(value=True)

checkbox_original = tk.Checkbutton(root, text="Originaldaten", variable=show_original, command=update_plot)
checkbox_original.pack(side=tk.LEFT)

checkbox_filtered_h = tk.Checkbutton(root, text="Gefilterte H-Werte", variable=show_filtered_h, command=update_plot)
checkbox_filtered_h.pack(side=tk.LEFT)

checkbox_filtered_b = tk.Checkbutton(root, text="Gefilterte B-Werte", variable=show_filtered_b, command=update_plot)
checkbox_filtered_b.pack(side=tk.LEFT)

checkbox_refiltered = tk.Checkbutton(root, text="Erneut gefilterte H-Werte", variable=show_refiltered, command=update_plot)
checkbox_refiltered.pack(side=tk.LEFT)

root.mainloop()

#%% 
from glob import glob
import os
import numpy as np
from astropy.time import Time
import pandas as pd 
from matplotlib import pyplot as plt
import scienceplots; plt.style.use('science')
from astroquery.fermi import FermiLAT
import matplotlib.dates as mdates  # Make sure this is imported
from tqdm import tqdm

def convert2db(data):
    """
    Convert SUPERSID voltages to dB.
    """
    return 20 * np.log10(data) + 1e-10 

def plot_time_window(data, mjd_time, grb_name, minutes_window=10):
    """
    Plots time against power for a 10-minute window around a specified MJD time.

    Parameters:
    - data (DataFrame): A pandas DataFrame containing 'time' and 'power' columns.
    - mjd_time (float): The central time in MJD.
    - minutes_window (int): The number of minutes before and after the MJD time to include in the plot.
    """
    if data['time'].dtype == 'object':  
        data['time'] = pd.to_datetime(data['time'])

    # Convert MJD to datetime
    central_time = Time(mjd_time, format='mjd').to_datetime()
    
    # Define the start and end times for the 10-minute window
    start_time = central_time - pd.Timedelta(minutes=minutes_window)
    end_time = central_time + pd.Timedelta(minutes=minutes_window)
    
    
    

    # Filter the data for the time window
    mask = (data['time'] >= start_time) & (data['time'] <= end_time)
    filtered_data = data.loc[mask]

    # Plot the filtered data
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_data['time'], filtered_data['power'], linestyle='-', color='k')
    
    plt.title(f'VLF data centered at {central_time} (±{minutes_window} minutes)')
    plt.xlabel('Time')
    plt.ylabel('Power')
    plt.axvline(central_time, color='r', linestyle='--', label=f'{grb_name}')
    
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_data_dictionary(data_dict, mjd_time, grb_name, index, minutes_window=10):
    """
    Plots multiple time series from a dictionary of dataframes, sharing the x-axis with no space between subplots.

    Parameters:
    - data_dict (dict): A dictionary where keys are identifiers and values are pandas DataFrames with 'time' and 'power' columns.
    - mjd_time (float): The central time in MJD.
    - grb_name (str): The name of the GRB event.
    - minutes_window (int): The number of minutes before and after the MJD time to include in the plot.
    - index (int): The index of the GRB event based on fluence (used for saving the plot).
    """
    labels = ['DHO', 'FTA', 'GBZ', 'NAA', 'NDT']

    # Convert MJD to datetime
    central_time = Time(mjd_time, format='mjd', scale='utc').to_datetime()
    
    # Define the start and end times for the time window
    start_time = central_time - pd.Timedelta(minutes=minutes_window)
    end_time = central_time + pd.Timedelta(minutes=minutes_window)

    if verbose:
        print('--- Plotted time window INFO ---')
        print(f'MJD time: {mjd_time}')
        print(f'Central time: {central_time}')
        print(f'Start time: {start_time}')
        print(f'End time: {end_time}')
    
    # Create a figure with subplots using gridspec with no space between subplots
    num_plots = len(data_dict)
    fig, axs = plt.subplots(num_plots, 1, figsize=(10, 6 + 2 * num_plots), 
                            sharex=True, gridspec_kw={'hspace': 0})

    for i, (key, data) in enumerate(data_dict.items()):
        ax = axs[i]

        # Convert 'time' column if needed
        if data['time'].dtype == 'object':
            data['time'] = pd.to_datetime(data['time'])

        # Filter for time window
        mask = (data['time'] >= start_time) & (data['time'] <= end_time)
        filtered_data = data.loc[mask]

        label = labels[i] if i < len(labels) else f'Data {key}'
        ax.plot(filtered_data['time'], filtered_data['power'], linestyle='-', color='k', label=label)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        ax.set_ylabel('Amplitude (dB)')
        ax.axvline(central_time, color='r', linestyle='--', label=f'{grb_name}')
        ax.grid(True)
        ax.legend()

        if i < num_plots - 1:
            ax.label_outer()



    axs[-1].set_xlabel('Time (UTC)')
    axs[-1].xaxis.set_tick_params(rotation=45)
    
    # Overall title for the figure
    fig.suptitle(f'VLF data centered at {central_time} (±{minutes_window} minutes) for {grb_name}', y=0.95)
    
    # Adjust layout to prevent overlap
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    #mkdir 
    if not os.path.exists('GRB_cands'):
        os.makedirs('GRB_cands')
    
    # plt.savefig(f'GRB_cands/{index}{grb_name}.png')
    plt.show()

verbose = True

# Load .csv paths 
# find all .csv files in in subdirectories
csv_files = sorted(glob(os.path.join('birr_data', '**', '*.csv'), recursive=True))
print('Number of .csv files:', len(csv_files))

# Grab the dates from the paths
birr_dates = []
for path in csv_files:
    split_path = path.split('/')
    year = split_path[-5]; month = split_path[-4]; day = split_path[-3]
    date = f'{year}-{month}-{day}'
    mjd = Time(date, format='iso', scale='utc').mjd
    birr_dates.append(mjd)

grb_names, grb_dates, grb_fluence = np.loadtxt('Summary_table.txt', usecols=(0, -1, 9), unpack=True, dtype=str, skiprows=4)
# Take top 10 GRBs with highest fluence, remove -999 values
# grb_fluence = grb_fluence.astype(float); sorted_indices = np.argsort(grb_fluence)[::-1]
# grb_dates = grb_dates[sorted_indices]; grb_names = grb_names[sorted_indices]; grb_fluence = grb_fluence[sorted_indices]
# print(grb_names); print(grb_fluence)

column_names = ['time', 'power'] 

# find the GRBs that were observed on the same day as the Birr data
for i in tqdm(range(len(grb_dates))):
    grb_day = int(float(grb_dates[i]))
    matching_indices = np.where(np.array(birr_dates).astype(int) == grb_day)[0]
    if len(matching_indices) > 0:
        if verbose: 
            print(f'{grb_names[i]} was observed on the same day as Birr data')
            print(f'GRB MJD: {grb_dates[i]}')
            print(f'Birr MJD: {birr_dates[matching_indices[0]]}')
            for j in matching_indices:
                print(f'Birr Data Path {j}: {csv_files[j]}')

        # --- Plot the data ---
        data_dictionary = {}

        for j in range(0, len(matching_indices)):
            data = pd.read_csv(csv_files[matching_indices[j]], skiprows=15, names=column_names, comment='#')
            # Check if time and power columns exist
            if 'time' not in data.columns or 'power' not in data.columns:
                print(f"Error⚠️: 'time' or 'power' column not found in {csv_files[matching_indices[j]]}")
                continue
            data_dictionary[f'{j}'] = data
        
        # convert power to dB
        for j in data_dictionary.keys():
            data_dictionary[j]['power'] = convert2db(data_dictionary[j]['power'])


        plot_data_dictionary(data_dictionary, float(grb_dates[i]), grb_names[i],  index=(i+1), minutes_window=30)
        # check if Fermi data is available
        
        print(f'Fermi data available for {grb_names[i]}')

# --- Plot fluence vs. time for any seen with the VLF --- 
# fluence_seen = []; dates = []
# for i in tqdm(range(len(grb_dates))):
#     grb_day = int(float(grb_dates[i]))
#     matching_indices = np.where(np.array(birr_dates).astype(int) == grb_day)[0]
#     if len(matching_indices) > 0:
#         fluence_seen.append(grb_fluence[i])
#         dates.append(grb_dates[i])
# from datetime import datetime
# # make sure fluence are non 0 values
# fluence_seen = np.array(fluence_seen)
# mask = fluence_seen != -999
# fluence_seen = fluence_seen[mask]
# dates = np.array(dates)[mask]

# # convert MJD to datetime

# # remove non-zero values
# fluence_seen = fluence_seen[fluence_seen != -999]
# dates = np.array(dates)[fluence_seen != -999]
# dates = [Time(date, format='mjd', scale='utc').to_datetime() for date in dates]

# # fluence as float
# # plt.axhline(np.mean(fluence_seen), color='r', linestyle='--', label='Mean Fluence %s erg/cm$^2$' % np.mean(fluence_seen))

# fluence_seen = fluence_seen.astype(float)
# plt.figure(figsize=(10, 8))
# plt.scatter(dates, fluence_seen, color='k', marker='o', s = 1)
# plt.yscale('log')
# plt.xlabel('Time (YYYY-MM)')
# plt.ylabel('Fluence (erg/cm$^2$)')
# plt.savefig('fluence_vs_time.png')
#%% 
import numpy as np 
from astroquery.heasarc import Heasarc
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.time import Time
import os

# Load paths from the file
paths = np.loadtxt('supersid_directories.txt', dtype=str)
csv_paths = [path for path in paths if 'csv' in path]

# Separate paths based on location
birr_data_path = [path for path in csv_paths if 'birr' in path]
dunsink_data_path = [path for path in csv_paths if 'dunsink' in path]

print('Number of Birr data paths:', len(birr_data_path))
print('Number of Dunsink data paths:', len(dunsink_data_path))

# --- Birr Dates --- 
birr_dates = []
for path in birr_data_path:
    year = path.split('/')[-5]; month = path.split('/')[-4]; day = path.split('/')[-3]
    date = f'{year}-{month}-{day}'
    birr_dates.append(date)

# --- GRB Database --- 
# Download the summary table, if needed
# os.system('wget https://user-web.icecube.wisc.edu/~grbweb_public/Summary_table.txt')
grb_names, grb_dates = np.loadtxt('Summary_table.txt', usecols=(0, -1), unpack=True, dtype=str, skiprows=4)

print('Total Number of GRBs:', len(grb_names))

# --- Convert Birr dates to MJD ---
time_objs = Time(birr_dates, format='iso', scale='utc')
birr_mjds = time_objs.mjd

observed_grbs = []
observed_dates = []
download_dates = []

for i in range(len(grb_dates)):
    grb_day = int(float(grb_dates[i]))  # Convert string to float first, then to int

    # Find indices where birr_mjds matches grb_day
    matching_indices = np.where(birr_mjds.astype(int) == grb_day)[0]

    if len(matching_indices) > 0:
        observed_grbs.append(grb_names[i])
        observed_dates.append(float(grb_dates[i]))
        # Append the corresponding Birr date and path to download_dates
        download_date = birr_dates[matching_indices[0]]
        download_path = birr_data_path[matching_indices[0]]
        download_dates.append((download_date, download_path))

print('Number of observed GRBs on days Birr has Data:', len(observed_dates))

# --- Download the data from linkes --- 
for i in range(len(download_dates)):
    date, path = download_dates[i]
    # check if already downloaded
    os.system(f'wget -r -np -nH --cut-dirs=3 -P birr_data/{date} {path}')
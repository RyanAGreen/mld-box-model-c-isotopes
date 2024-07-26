import PyCO2SYS as pyco2
import numpy as np
import pandas as pd 
import os

def load_real_data(prefix, simulation_length_years):
    """
    Load and process real data for temperature and salinity from a .h5 file.

    Parameters:
    - prefix (str): Prefix for the columns containing temperature and salinity data.
    - simulation_length_years (int): Total number of years for the simulation.

    Returns:
    - temperature (array): Temperature profile (°C) for each day of the simulation period.
    - salinity (array): Salinity profile (PSU) for each day of the simulation period.
    """
    def loop_years(vec):
        slope = np.linspace(0, (vec[0] - vec[364]), 365)
        vec = vec + slope
        return np.hstack((vec, vec))

    # Define the data directory and file path
    DATADIR = os.path.join(os.path.dirname(__file__), "indata")
    file_path = os.path.join(DATADIR, "mercator_tseries.h5")

    # Load the .h5 file into a DataFrame
    df = pd.read_hdf(file_path)

    # Extract temperature and salinity data and process
    temp_data = loop_years(df[prefix + "temp"][:365].values)
    salt_data = loop_years(df[prefix + "salt"][:365].values)

    # Repeat profiles for the total simulation length
    total_days = simulation_length_years * 365
    temperature = np.tile(temp_data, (total_days // 365) + 1)[:total_days]
    salinity = np.tile(salt_data, (total_days // 365) + 1)[:total_days]

    return temperature, salinity




def load_seasonal_forcings(simulation_length_years):
    """
    Load seasonal forcings for temperature and salinity for a given number of years with daily data.
    This function generates seasonal profiles for the US East Coast.

    Parameters:
    - simulation_length_years (int): Total number of years for the simulation.

    Returns:
    - temperature (array): Temperature profile (°C) for each day of the simulation period.
    - salinity (array): Salinity profile (PSU) for each day of the simulation period.
    """
    days_in_year = 365
    days = np.arange(days_in_year)

    # Generate temperature profile for one year
    temp_mean = 15  # Mean temperature
    temp_amplitude = 7.5  # Amplitude of temperature variation to match the figure
    temp_phase_shift = 180  # Phase shift to align with peak temperature in late August
    temperature_one_year = temp_mean + temp_amplitude * np.sin(2 * np.pi * (days - temp_phase_shift) / days_in_year)

    # Generate salinity profile for one year
    sal_mean = 33.5  # Mean salinity
    sal_amplitude = 0.5  # Amplitude of salinity variation to match the figure
    sal_phase_shift = 31  # Phase shift to align with minimum salinity in July
    salinity_one_year = sal_mean + sal_amplitude * np.sin(2 * np.pi * (days + sal_phase_shift) / days_in_year)
    
    # Repeat profiles for the total simulation length
    total_days = simulation_length_years * days_in_year
    temperature = np.tile(temperature_one_year, simulation_length_years)
    salinity = np.tile(salinity_one_year, simulation_length_years)

    return temperature, salinity


def calc_talk(salt, pref):
    """
    Calculate Total Alkalinity (TA) based on salinity and region.

    Parameters:
    - salt (float): Salinity used to calculate TA.
    - pref (str): Region of the US East Coast. Options are:
                  'se' (South Atlantic Bight),
                  'me' (Mid Atlantic Bight),
                  'ne' (North Atlantic outside Gulf of Maine).

    Returns:
    - talk (float): Calculated Total Alkalinity.
    """
    if pref == "se":
        talk = 48.7 * salt + 608.8
    elif pref == "me":
        talk = 46.6 * salt + 670.6
    elif pref == "ne":
        talk = 39.1 * salt + 932.7
    else:
        raise ValueError("Invalid region code. Use 'se', 'me', or 'ne'.")
    return talk

def compute_initial_conditions(pCO2, alk, temp, sal):
    """
    Compute chemical properties using PyCO2SYS.

    Parameters:
    - pCO2 (float): Surface ocean pCO2 concentration.
    - alk (float): Alkalinity concentration.

    Returns:
    - dict: A dictionary containing various chemical properties.
    """
    kwargs = {
        "par1": alk,
        "par2": pCO2,
        "par1_type": 1,  # Alkalinity
        "par2_type": 4,  # pCO2
        "temperature": temp,
        "salinity": sal,
    }
    return pyco2.sys(**kwargs)
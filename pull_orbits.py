from astropy.coordinates import SkyCoord
from astropy.time import Time
from astroquery.jplhorizons import Horizons
from datetime import datetime, timedelta
import numpy as np
import csv
import json


def get_coords_for_single_revolution(obj_id):

    # print(f'Getting coordinates for {obj_id}')

    # Define the time range for which to retrieve the position vectors
    horizons_obj, period = calc_period(obj_id)

    horizons_date_format = '%Y-%m-%d %H:%M:%S'

    # Start date is today
    current_time = datetime.now()
    start_date = current_time.strftime(horizons_date_format)

    # End date is today + one period
    period_as_days = period * 365.25
    stop_date = (current_time + timedelta(days=period_as_days)).strftime(horizons_date_format)
    
    # 100 steps
    step = '100'

    epochs_dict = {'start': start_date, 'stop': stop_date, 'step': step}
    
    # print(epochs_dict)

    q = Horizons(id=obj_id, location='500@Sun', epochs=epochs_dict)

    # Retrieve the position vectors from Horizons in the 'earth' reference plane
    tab = q.vectors(refplane='earth')

    # Define an array of observation times corresponding to the epochs_dict
    times = Time(tab['datetime_jd'].quantity, format='jd')

    # Create a SkyCoord object using the retrieved vectors and the array of times
    return SkyCoord(tab['x'].quantity, tab['y'].quantity, tab['z'].quantity,
                    representation_type='cartesian', frame='icrs',
                    obstime=times)

def calc_period(obj_id):
    # Create a Horizons object for the target 'Ceres'
    horizons_obj = Horizons(id=obj_id, location='500@Sun')

    # Query the orbital elements
    elements = horizons_obj.elements()

    # Extract the semi-major axis (in AU)
    semi_major_axis = elements['a'][0]

    # Calculate the orbital period (in years) using Kepler's Third Law
    orbital_period = np.sqrt(semi_major_axis**3)

    return horizons_obj, orbital_period

def main():
    with open('asteroids_test.csv', mode='r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)

        asteroid_dict_list = []

        for name, obj_id in csv_reader:
            sky_coords = get_coords_for_single_revolution(obj_id)
            print(f'Got coordinates for {name} ({obj_id})')

            coords = [{'x': float(coord.x.value), 'y': float(coord.y.value), 'z': float(coord.z.value)} for coord in sky_coords]
            new_asteroid_dict = { 'name': name, 'obj_id': obj_id, 'coords_au': coords }
            
            asteroid_dict_list.append(new_asteroid_dict)

    json_file_path = 'asteroid_positions.json'
    with open(json_file_path, 'w') as json_file:
        json.dump(asteroid_dict_list, json_file, indent=4)

    print(f"Data successfully written to {json_file_path}")

if __name__ == "__main__":
    main()
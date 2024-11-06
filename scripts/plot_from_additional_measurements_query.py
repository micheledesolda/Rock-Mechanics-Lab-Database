# scripts/plot_from_additional_measurements_query.py
from rock_mechanics_lab_database.daos.experiment_dao import ExperimentDao
import os
import matplotlib.pyplot as plt


def main():
    experimentDao = ExperimentDao()
    uw_sequence_name = "001_run_in_10MPa"
    experiment_id = "s0108sw06car102030"

    # Define the range of uw_numbers you want to plot
    start_uw = 0
    end_uw = 500

    # Retrieve the ultrasonic waveforms data
    uw_dict = experimentDao.find_additional_measurements(experiment_id=experiment_id, 
                                                         measurement_type="ultrasonic_waveforms",
                                                         measurement_sequence_id=uw_sequence_name, 
                                                         start_uw=start_uw, end_uw=end_uw)

    if not uw_dict:
        print("No data found for the specified range.")
        return

    metadata = uw_dict["properties"]
    data = uw_dict["data"]

    # Assuming each row in data is a waveform and the first column is time
    if not data or not data[0]:
        print("No data available for plotting.")
        return


    # Plotting the waveforms
    for waveform in data:
        plt.plot(waveform)

    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title(f'Ultrasonic Waveforms from {uw_sequence_name}\nWave numbers: {start_uw} to {end_uw}')
    plt.show()

    print("Query to database and plot work.")


if __name__ == "__main__":
    main()

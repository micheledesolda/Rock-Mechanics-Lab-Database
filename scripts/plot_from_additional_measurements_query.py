# scripts/plot_from_additional_measurements_query.py
from daos.experiment_dao import ExperimentDao
import os
import matplotlib.pyplot as plt


def main():
    experimentDao = ExperimentDao()
    dirname = os.path.dirname(__file__)
    test_dir = os.path.join(dirname, '../tests/test_data')
    file_name = "s0108sw06car102030.tsv"
    experiment_name = file_name.split(".")[0]

    # Define the range of uw_numbers you want to plot
    start_uw = 0
    end_uw = 500

    # Retrieve the ultrasonic waveforms data
    uw_dict = experimentDao.find_additional_measurements(experiment_id=experiment_name, measurement_type="ultrasonic_waveforms", start_uw=start_uw, end_uw=end_uw)

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
    plt.title(f'Plot of Ultrasonic Waveforms from {start_uw} to {end_uw}')
    plt.show()

    print("Query to database and plot work.")


if __name__ == "__main__":
    main()

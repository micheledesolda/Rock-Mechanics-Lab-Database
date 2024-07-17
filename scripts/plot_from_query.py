# scripts/plot_from_query.py
from daos.experiment_dao import ExperimentDao
import os
import matplotlib.pyplot as plt


experimentDao = ExperimentDao()
dirname = os.path.dirname(__file__)
test_dir = os.path.join(dirname, '../tests/test_data')
file_name = "s0108sw06car102030.tdms"
experiment_name = file_name.split(".")[0]
experiment_path = os.path.join(test_dir,file_name)

x_field = "Time"
y_field = "Vertical Load"
x_dict = experimentDao.find_centralized_measurements(experiment_id=experiment_name, group_name="ADC", channel_name=x_field)
y_dict = experimentDao.find_centralized_measurements(experiment_id=experiment_name, group_name="ADC", channel_name=y_field)
x_values = x_dict["data"]
y_values = y_dict["data"]

# Create scatter plot
plt.plot(x_values, y_values)
plt.xlabel(x_field)
plt.ylabel(y_field)
plt.title(f'Plot of {x_field} vs {y_field}')
plt.show()

print("Database created and data added successfully.")
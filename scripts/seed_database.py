import os
from daos.experiment_dao import ExperimentDao
from daos.block_dao import BlockDao
from daos.gouge_dao import GougeDao
from daos.sensor_dao import SensorDao
from daos.core_sample_dao import CoreSampleDao
from daos.machine_dao import MachineDao
from utils.mongo_utils import is_mongodb_running, start_mongodb

def seed_database():

    print("Seeding database...")
    seed_machines()
    seed_sensors()
    seed_gouges()
    seed_coresamples()
    seed_blocks()
    seed_experiments()

    print("Seeding database: done")

def seed_machines():
    machineDao = MachineDao()
    machine_id = "Brava2"
    machine_type = "Biaxial Apparatus"
    creation_date = "Wednesday, March 15, 2023 9:52:34 AM"
    
    pistons = {
        "vertical": {
            "calibration": [
                {
                    "date": creation_date,
                    "coefficients": [ -0.5043737 ,   4.27584024, -11.70546934,   5.45745069,
                                    29.43390033, -60.90428874,  60.98729795, 124.19783947,
                                    -0.47000267]
                }
            ],
            "stiffness": [
                {
                    "date": creation_date,
                    "coefficients": [ 3.35241499e-30, -9.37367134e-27,  1.19440060e-23, -9.17845027e-21,
                                      4.74088379e-18, -1.73500082e-15,  4.61575497e-13, -9.00528796e-11,
                                      1.28295415e-08, -1.31327065e-06,  9.38895324e-05, -4.50176164e-03,
                                      1.38008389e-01, -2.63525139e+00,  3.57750394e+01,  1.71503762e+01]
                }
            ]
        },
        "horizontal": {
            "calibration": [
                {
                    "date": creation_date,
                    "coefficients": [-4.63355231e-02, -2.57055418e+00,  2.63055688e+01, -9.61932787e+01,
                                     1.64685122e+02, -1.33648859e+02,  4.66773182e+01,  1.63975941e+02,
                                     9.32438525e-02]
                }
            ],
            "stiffness": [
                {
                    "date": creation_date,
                    "coefficients": [ 2.43021220e-31, -7.73507440e-28,  1.10791696e-24, -9.43050473e-22,
                                      5.30556343e-19, -2.07533887e-16,  5.77817817e-14, -1.15148744e-11,
                                      1.62528123e-09, -1.57483543e-07,  9.75756659e-06, -3.16390679e-04,
                                      1.96801181e-04,  2.69515293e-01,  5.53939566e+00,  4.21560673e+01]
                }
            ]
        }
    }

    machineDao.create(machine_id, machine_type, pistons)

def seed_coresamples():
    coreSampleDao = CoreSampleDao()
    coreSampleDao.create(core_sample_id="san_donato_1", material="granite", dimensions={"diameter": 5.0, "height": 10.0})
    coreSampleDao.create(core_sample_id="san_donato_13", material="dolomite", dimensions={"diameter": 5.0, "height": 10.0})

def seed_gouges():
    gougeDao = GougeDao()
    gougeDao.create(gouge_id="mont1", material="montmorillonite", grain_size_mum=125)
    gougeDao.create(gouge_id="minusil", material="quartz", grain_size_mum=40)
    gougeDao.create(gouge_id="F110", material="quartz", grain_size_mum=110)

def seed_sensors():
    available_sensors = [
        {"sensor_id": "PZT_1", "sensor_type": "piezoelectric", "model": "P-871.20", "resonance_frequency": 1.0, "properties": {"material": "PZT"}},
        {"sensor_id": "PZT_2", "sensor_type": "piezoelectric", "model": "P-871.30", "resonance_frequency": 3.0, "properties": {"material": "PZT"}},
        {"sensor_id": "PZT_3", "sensor_type": "piezoelectric", "model": "P-871.40", "resonance_frequency": 5.0, "properties": {"material": "PZT"}}
    ]
    sensorDao = SensorDao()
    for sensor in available_sensors:
        sensorDao.create(**sensor)

def seed_blocks():
    blockDao = BlockDao()
    blockDao.create(block_id="paglialberi_1", material="steel", dimensions={"width": 2.0, "height": 2.0, "depth": 4.8}, sensor_rail_width=0.5),
    blockDao.create(block_id="paglialberi_2", material="steel", dimensions={"width": 2.0, "height": 2.0, "depth": 4.8}, sensor_rail_width=0.5),
    blockDao.create(block_id="mem_1", material="steel", dimensions={"width": 2.0, "height": 2.0, "depth": 4.8}, sensor_rail_width=0.5)        
    blockDao.add_sensor(block_id="paglialberi_1", sensor_id="PZT_1", sensor_name="S_left", position={"x": 0.5, "y": 1.0, "z": 0.2}, orientation="left", calibration="Calibration S_left")
    blockDao.add_sensor(block_id="paglialberi_1", sensor_id="PZT_1", sensor_name="S_right", position={"x": 0.7, "y": 1.0, "z": 0.2}, orientation="up", calibration="Calibration S_right")
    blockDao.add_sensor(block_id="paglialberi_2", sensor_id="PZT_2", sensor_name="P", position={"x": 1.5, "y": 1.0, "z": 0.2}, orientation=None, calibration="Calibration P")        


def seed_experiments():
    experimentDao = ExperimentDao()

    # it is possible to insert an experiment providing explictely all the fields or part of them
    experimentDao.create_experiment(experiment_id="test experiment_created_manually", 
                                    experiment_type="triaxial", 
                                    core_sample_id="san_donato_1", 
                                    centralized_measurements=[{"time_s":[1,2,3]},
                                                              {"displacement_mum":[3,4.5,6.3]}], 
                                    additional_measurements=[{"amplitude_uw_mum":[10, 11, 12]},
                                                             {"emission_rate_ae":[12,5,28,0,0,31]}])

    experimentDao.create_experiment(experiment_id="another test experiment_created_manually", 
                                    experiment_type="Double Direct Shear", 
                                    gouges=[{"gouge_id":"mont1","thickness_mm":0.3}], 
                                    centralized_measurements=[{"time_s":[1,2,3]},
                                                              {"displacement_mum":[3,4.5,6.3]}], 
                                    additional_measurements=[{"amplitude_uw_mum":[10, 11, 12]},
                                                             {"emission_rate_ae":[12,5,28,0,0,31]}])

    # Here a specific implementation in case of tdms files, as those coming LabView interface of from Brava2
    dirname = os.path.dirname(__file__)
    test_dir = os.path.join(dirname, '../tests/test_data')
    file_name = "s0108sw06car102030.tdms"
    experiment_name = file_name.split(".")[0]
    experiment_path = os.path.join(test_dir,file_name)

    experiment_id = experimentDao.create_experiment(experiment_id=experiment_name, 
                                                    experiment_type="double direct shear", 
                                                    blocks=[{"block_id":"paglialberi_1","position":"left"}], 
                                                    gouges=[], 
                                                    centralized_measurements=[1, 2, 3],  
                                                    additional_measurements=[{"amplitude_uw_mum":[10, 11, 12]},
                                                                             {"emission_rate_ae":[12,5,28,0,0,31]}])

    # Example usage to add blocks, gouge or measurement to the experiments
    experimentDao.add_gouge(experiment_id=experiment_id,gouge_id="mont1",thickness_mm=0.3)
    experimentDao.add_block(experiment_id=experiment_id, block_id="paglialberi_2",position="right")
    # Measurement Data can be added after the experiment creation
    # NB: adding centralized measurements will overwrite the previous one!!!
    experimentDao.add_centralized_measurements_from_tdms_file(experiment_id=experiment_id,file_path=experiment_path)
    # here as additional_measurements we add ultrasonic waveforms
    file_name = "001_run_in_10MPa.bscan.tsv"
    file_path = os.path.join(test_dir,file_name)
    experimentDao.add_utrasonic_waveforms_from_tsv_file(file_path=file_path, experiment_id=experiment_id)

    # The file can be created directly from the tdms file. In this case, the file name will be the experiment_id (without extension)
    file_name = "s0074sa03min50.tdms"
    experiment_path = os.path.join(test_dir,file_name)
    experiment_id = experimentDao.create_experiment_from_file(file_path=experiment_path)
    experimentDao.add_gouge(experiment_id=experiment_id,gouge_id="minusil",thickness_mm=0.3)
    experimentDao.add_block(experiment_id=experiment_id, block_id="paglialberi_1",position="right")
    experimentDao.add_block(experiment_id=experiment_id, block_id="mem_1",position="left")

## Actua code to seed the database

if __name__ == "__main__":
    seed_database()

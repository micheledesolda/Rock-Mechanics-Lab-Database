# src/scripts/seed_database.py
import os
from daos.experiment_dao import ExperimentDao
from daos.block_dao import BlockDao
from daos.gouge_dao import GougeDao
from daos.sensor_dao import SensorDao
from daos.core_sample_dao import CoreSampleDao

def seed_machines():
    pass

def seed_coresamples():
    coreSampleDao = CoreSampleDao()
    coreSampleDao.create(core_sample_id="san_donato_1", material="granite", dimensions={"diameter": 5.0, "height": 10.0})

def seed_gouges():
    gougeDao = GougeDao()
    gougeDao.create(gouge_id="mont1", material="montmorillonite", grain_size_mum=125)

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
    dirname = os.path.dirname(__file__)
    test_dir = os.path.join(dirname, '../../tests')
    experiment_name = "s0108sw06car102030.tdms"
    experiment_path = os.path.join(test_dir,experiment_name)
    experiment_id = experimentDao.create(experiment_id=experiment_path, experiment_type="double direct shear", blocks=[{"block_id":"paglialberi_1","position":"left"}], gouges=[{"gouge_id":"mont1","thickness_mm":0.3}], centralized_measurements=[1, 2, 3],  additional_measurements=[{"amplitude_uw_mum":[10, 11, 12]},{"emission_rate_ae":[12,5,28,0,0,31]}])
    experimentDao.create(experiment_id="2", experiment_type="triaxial", core_sample_id=["san_donato_1"], centralized_measurements=[{"time_s":[1,2,3]},{"displacement_mum":[3,4.5,6.3]}], additional_measurements=[{"amplitude_uw_mum":[10, 11, 12]},{"emission_rate_ae":[12,5,28,0,0,31]}])

    # Example usage to add blocks, gouge or measurement to the experiments
    experimentDao.add_block(experiment_id=experiment_id, block_id="paglialberi_1",position="left")
    experimentDao.add_gouge(experiment_id=experiment_id,gouge_id="mont1",thickness_mm=0.3)
    experimentDao.add_block(experiment_id=experiment_id, block_id="paglialberi_2",position="right")
    # Data can be added after the experiment creation
    experimentDao.add_centralized_measurements_from_tdms_file(experiment_id=experiment_id,file_path=experiment_path)

if __name__ == "__main__":
    seed_machines()
    seed_sensors()
    seed_gouges()
    seed_coresamples()
    seed_blocks()
    seed_experiments()



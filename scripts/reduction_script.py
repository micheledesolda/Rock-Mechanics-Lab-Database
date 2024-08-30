# scripts/reduction_script.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from services.machine_service import MachineService
from services.experiment_service import ExperimentService
from services.block_service import BlockService

ms = MachineService()
es = ExperimentService()
bs = BlockService()

def fetch_load_measurements(experiment_id, piston_name, group_name='ADC'):
    """
    Fetch load measurements for a given piston.

    Parameters:
    experiment_id (str): The ID of the experiment.
    piston_name (str): The name of the piston ('Vertical' or 'Horizontal').
    group_name (str): The group name for measurements (default 'ADC').

    Returns:
    np.ndarray: Load measurements in volts.
    """
    load_measurements = es.get_centralized_measurements(experiment_id=experiment_id, group_name=group_name, channel_name=piston_name + " Load")
    load_recorded = np.array(load_measurements['data'])
    visualization_slope = load_measurements['properties']['Slope']
    intercept = load_measurements['properties']['Intercept']
    offset = intercept/visualization_slope
    load_volt = load_recorded + offset

    print(f"fetch_load_measurements - load_volt: {load_volt}")

    return load_volt

def apply_calibration(machine_id, piston_name, load_volt, experiment_date):
    """
    Apply calibration to load measurements.

    Parameters:
    machine_id (str): The ID of the machine.
    piston_name (str): The name of the piston ('Vertical' or 'Horizontal').
    load_volt (np.ndarray): Load measurements in volts.
    experiment_date (str): The date of the experiment.

    Returns:
    np.ndarray: Load measurements in kN.
    """
    load_kN = ms.apply_calibration(machine_id=machine_id, 
                                   piston_name=piston_name, 
                                   voltage=load_volt, 
                                   experiment_date=experiment_date)
    #plt.plot(load_kN)

    return load_kN

def fetch_displacement_measurements(experiment_id, piston_name, group_name='ADC'):
    """
    Fetch displacement measurements for a given type.

    Parameters:
    experiment_id (str): The ID of the experiment.
    displacement_type (str): The type of displacement ('Vertical' or 'Horizontal').
    group_name (str): The group name for measurements (default 'ADC').

    Returns:
    np.ndarray: Displacement measurements in mm
    """
    displacement_measurements = es.get_centralized_measurements(experiment_id=experiment_id, 
                                                                group_name=group_name, 
                                                                channel_name=piston_name + " Displacement")
    displacement_recorded = np.array(displacement_measurements['data'])
    slope = displacement_measurements['properties']['Slope']
    intercept = displacement_measurements['properties']['Intercept']
    displacement_mum = slope * displacement_recorded + intercept       # the LVDT calibration in Brava2 provide measurement in micrometers. Modify accordingly for different machine
    displacement_mm = 1e-3 * displacement_mum

    return displacement_mm

def detect_touch_point(force_readings, check_up2load=10):
    """
    Detects the touch point where the force readings consistently stay above the moving average.

    Parameters:
    - force_readings: [kN] The time series data of force readings.
    - check_up2load: [kN] touch point is searched in the segment before the first occurrence of this value
    
    Returns:
    - The index of the touch point.
    """
    if force_readings is None:
        print("detect_touch_point - force_readings is None")
    else:
        print(f"detect_touch_point - force_readings: {force_readings[:10]}")  # print first 10 elements

    min_list = []
    max_list = []
    average_list = []
    idx_lim = np.argmax(force_readings > check_up2load)
    force_readings = force_readings[:idx_lim] - force_readings[0]
    for N in range(1, len(force_readings)):
        min_list.append(np.min(force_readings[:N]))
        max_list.append(np.max(force_readings[:N]))
        average_list.append(np.mean(force_readings[:N]))
    
    for i in range(1, len(average_list)):
        if all(force_readings[j] > average_list[j] for j in range(i, len(average_list))):
            print(f"Touch point detected at index: {i}")
            return i + 1  # Return the index adjusted to the original data
    
    return -1  # Return -1 if no touch point is detected

def machine_stiffness_correction(force, disp, k):
    """
    Apply correction to displacement data for the stiffness of the machine

    Parameters:
    stress (np.ndarray): The force data array.
    disp (np.ndarray): The displacement data array.
    k (float or np.ndarray): The stiffness value (scalar or array).

    Returns:
    np.ndarray: Elastic corrected displacement data.
    """
    # Convert scalar k to an array if it is not already an array
    if np.isscalar(k):
        k = k
    else:
        k = k[:-1]

    # Increments in elastic distortion
    dload = (force[1:] - force[:-1]) / k
    # Increments in total displacement
    ddisp = disp[1:] - disp[:-1]
    # Subtract elastic distortion from total displacement
    displacement_corrected = np.hstack([0, np.cumsum(ddisp - dload)])
    return displacement_corrected

def preprocessing_for_piston_noise(measurement):
    """
    Preprocess the load measurements to remove noise.

    Parameters:
    measurement (np.ndarray): Load measurements in kN.

    Returns:
    np.ndarray: Preprocessed measurements.
    """
    touch_point = detect_touch_point(measurement)
    if touch_point == -1:
        print("preprocessing_for_piston_noise - touch_point not detected, returning original measurement")
        return measurement
    measurement = measurement - measurement[touch_point]  # Remove noise before load is applied
    measurement[:touch_point] = measurement[:touch_point] * 0
    measurement = np.where(measurement > 0, measurement, 0)
    return measurement

def calculate_shear_stress(load_kN, gouge_area):
    """
    Calculate shear stress from load measurements.

    Parameters:
    load_kN (np.ndarray): Load measurements in kN.
    gouge_area (float): Gouge area in square meters.

    Returns:
    np.ndarray: Shear stress in MPa.
    """
    shear_stress_MPa = 1e-3 * load_kN / (2 * gouge_area)  # Conversion to MPa
    return shear_stress_MPa

def calculate_normal_stress(load_kN, gouge_area):
    """
    Calculate normal stress from load measurements.

    Parameters:
    load_kN (np.ndarray): Load measurements in kN.
    gouge_area (float): Gouge area in square meters.

    Returns:
    np.ndarray: Normal stress in MPa.
    """
    normal_stress_MPa = 1e-3 * load_kN / gouge_area  # Conversion to MPa
    return normal_stress_MPa

def calculate_load_point_displacement(v_displacement_mm, v_touch_point):
    """
    Calculate load point displacement from horizontal displacement.

    Parameters:
    h_displacement (np.ndarray): Horizontal displacement measurements.

    Returns:
    np.ndarray: Load point displacement in mm.
    """
    load_point_displacement_mm = v_displacement_mm - v_displacement_mm[v_touch_point] # [mum]
    load_point_displacement_mm[:v_touch_point] = load_point_displacement_mm[:v_touch_point]*0
 
    return load_point_displacement_mm

def calculate_layer_thickness(h_displacement_mm, layer_thickness_measured_mm, layer_thickness_measured_point):
    """
    Calculate layer thickness from vertical displacement.

    Parameters:
    v_displacement (np.ndarray): Vertical displacement measurements.
    rec_lt (int): Record number where layer thickness was measured.
    val_lt (float): Measured layer thickness value in mm.

    Returns:
    np.ndarray: Layer thickness in mm.

    """

    print(layer_thickness_measured_point)
    h_displacement_zeroed_mm = h_displacement_mm - h_displacement_mm[layer_thickness_measured_point]
    layer_thickness_mm = h_displacement_zeroed_mm + layer_thickness_measured_mm
    layer_thickness_mm = np.where(layer_thickness_mm < layer_thickness_measured_mm, layer_thickness_mm, layer_thickness_measured_mm)

    return layer_thickness_mm

def process_vertical_load_measurements(experiment_id, 
                                       machine_id, 
                                       experiment_date, 
                                       gouge_area, 
                                       group_name='ADC', 
                                       piston_name="Vertical"):
    """
    Process vertical load measurements to calculate shear stress.

    Parameters:
    experiment_id (str): The ID of the experiment.
    machine_id (str): The ID of the machine.
    experiment_date (str): The date of the experiment.
    gouge_area (float): Gouge area in square meters.
    group_name (str): The group name for measurements (default 'ADC').
    piston_name (str): The name of the piston (default 'Vertical').

    Returns:
    np.ndarray: Shear stress in MPa.
    """
    v_load_volt = fetch_load_measurements(experiment_id=experiment_id, 
                                          piston_name=piston_name, 
                                          group_name=group_name)
    v_load_kN = apply_calibration(machine_id=machine_id,  
                                  piston_name=piston_name, 
                                  load_volt=v_load_volt,
                                  experiment_date=experiment_date)
    v_load_kN_preprocessed = preprocessing_for_piston_noise(measurement=v_load_kN)
    shear_stress_MPa = calculate_shear_stress(v_load_kN_preprocessed, gouge_area)
    return shear_stress_MPa

def process_horizontal_load_measurements(experiment_id, 
                                         machine_id, 
                                         experiment_date, 
                                         gouge_area, 
                                         group_name='ADC', 
                                         piston_name="Horizontal"):
    """
    Process horizontal load measurements to calculate normal stress.

    Parameters:
    experiment_id (str): The ID of the experiment.
    machine_id (str): The ID of the machine.
    experiment_date (str): The date of the experiment.
    gouge_area (float): Gouge area in square meters.
    group_name (str): The group name for measurements (default 'ADC').
    piston_name (str): The name of the piston (default 'Horizontal').

    Returns:
    np.ndarray: Normal stress in MPa.
    """
    h_load_volt = fetch_load_measurements(experiment_id=experiment_id, 
                                          piston_name=piston_name, 
                                          group_name=group_name)
    h_load_kN = apply_calibration(machine_id=machine_id,  
                                  piston_name=piston_name, 
                                  load_volt=h_load_volt,
                                  experiment_date=experiment_date)
    h_load_kN_preprocessed = preprocessing_for_piston_noise(measurement=h_load_kN)
    normal_stress_MPa = calculate_normal_stress(h_load_kN_preprocessed, gouge_area)
    return normal_stress_MPa

def process_load_point_displacement(experiment_id, 
                                    machine_id, 
                                    experiment_date, 
                                    group_name='ADC',
                                    piston_name = "Vertical"):
    """
    Process horizontal displacement measurements to calculate load point displacement.

    Parameters:
    experiment_id (str): The ID of the experiment.
    machine_id (str): The ID of the machine.
    experiment_date (str): The date of the experiment.
    group_name (str): The group name for measurements (default 'ADC').

    Returns:
    np.ndarray: Load point displacement in mm.
    """
    v_displacement_mm = fetch_displacement_measurements(experiment_id=experiment_id, 
                                                     piston_name=piston_name, 
                                                     group_name=group_name)
    v_load_volt = fetch_load_measurements(experiment_id=experiment_id, 
                                          piston_name=piston_name, 
                                          group_name=group_name)
    v_load_kN = apply_calibration(machine_id=machine_id, 
                                  piston_name=piston_name, 
                                  load_volt=v_load_volt,
                                  experiment_date=experiment_date)
    
    v_touch_point = detect_touch_point(v_load_kN)
    load_point_displacement_mm = calculate_load_point_displacement(v_displacement_mm, 
                                                                v_touch_point=v_touch_point)
  
    # Fetch stifness correction for the stretch of the vertical frame # 
    v_stiffness = ms.apply_stiffness_correction(machine_id=machine_id, 
                                                piston_name='Vertical', 
                                                force = v_load_kN, 
                                                experiment_date=experiment_date)
    # Load point trend corrected for the machine stiffness 
    load_point_displacement_corrected_mm = machine_stiffness_correction(v_load_kN, load_point_displacement_mm, v_stiffness)

    return load_point_displacement_corrected_mm

def process_layer_thickness(experiment_id, 
                            machine_id,
                            experiment_date,
                            layer_thickness_measured_mm,
                            layer_thickness_measured_point, 
                            group_name='ADC',
                            piston_name="Horizontal"):
    """
    Process vertical displacement measurements to calculate layer thickness.

    Parameters:
    experiment_id (str): The ID of the experiment.
    rec_lt (int): Record number where layer thickness was measured.
    val_lt (float): Measured layer thickness value in mm.
    group_name (str): The group name for measurements (default 'ADC').

    Returns:
    np.ndarray: Layer thickness in mm.
    """
    h_displacement_mm = fetch_displacement_measurements(experiment_id=experiment_id, 
                                                     piston_name=piston_name, 
                                                     group_name=group_name)
    
    h_load_volt = fetch_load_measurements(experiment_id=experiment_id, 
                                          piston_name=piston_name, 
                                          group_name=group_name)
    
    h_load_kN = apply_calibration(machine_id=machine_id, 
                                  piston_name=piston_name, 
                                  load_volt=h_load_volt,
                                  experiment_date=experiment_date)

    # in case the layer_thickness_measured_point is conventionally put to "zero",
    # it means the layer_thickness_measured value is the one from bench measurement
    # in this case, we assume that is the value the layer thickness has when 
    # the horizont piston touch the sample
    if layer_thickness_measured_point == 0:
        layer_thickness_measured_point = detect_touch_point(h_load_kN)

    # Fetch stifness correction for the stretch of the vertical frame # 
    h_stiffness = ms.apply_stiffness_correction(machine_id=machine_id, 
                                                piston_name=piston_name, 
                                                force = h_load_kN, 
                                                experiment_date=experiment_date)
    
    #Layer thickness trend corrected for the machine stiffness 
    h_displacement_corrected_mm = machine_stiffness_correction(h_load_kN, h_displacement_mm, h_stiffness)

    layer_thickness_corrected_mm = calculate_layer_thickness(h_displacement_mm=-h_displacement_corrected_mm, 
                                                layer_thickness_measured_mm= layer_thickness_measured_mm, 
                                                layer_thickness_measured_point= layer_thickness_measured_point)

    return layer_thickness_corrected_mm


def calculate_gouge_area_from_blocks_dimensions(experiment_id):
    
    # Query for block dimensions
    blocks = es.get_blocks(experiment_id=experiment_id)
    if not blocks:
        # Add the blocks used in the experiment if it is not been done already
        es.add_block(experiment_id=experiment_id, block_id="paglialberi_1",position="left"),
        es.add_block(experiment_id=experiment_id, block_id="central_1",position="central"),
        es.add_block(experiment_id=experiment_id, block_id="paglialberi_2",position="right")
        blocks = es.get_blocks(experiment_id=experiment_id)

    # Calculate the gouge area
    lateral_block_dimensions = blocks[0]["dimensions"]
    gouge_area_mm2 = lateral_block_dimensions['width'] * lateral_block_dimensions['height']  
    gouge_area_m2 = 1e-6 * gouge_area_mm2    # covnersion to [m^2]
    return gouge_area_m2

def main():
    experiment_id = 's0037sa03min12'
    machine_id = 'Brava2'
    experiment_info = es.get_experiment_by_id(experiment_id)
    experiment_date = experiment_info['Start_Datetime']
    gouge_area = calculate_gouge_area_from_blocks_dimensions(experiment_id=experiment_id)

    # This must be the input of a manual measure
    # if layer_thickness_measured_point == 0 it is assumed is the nominal bench measurement
    layer_thickness_measured_mm = 6  # Example layer thickness value in mm
    layer_thickness_measured_point = 0  # Example record number for layer thickness
    
    shear_stress_MPa = process_vertical_load_measurements(experiment_id=experiment_id, 
                                                          machine_id=machine_id, 
                                                          experiment_date=experiment_date, 
                                                          gouge_area=gouge_area)
    
    normal_stress_MPa = process_horizontal_load_measurements(experiment_id=experiment_id, 
                                                             machine_id=machine_id, 
                                                             experiment_date=experiment_date, 
                                                             gouge_area=gouge_area)
    
    load_point_displacement_mm = process_load_point_displacement(experiment_id=experiment_id, 
                                                              machine_id=machine_id, 
                                                              experiment_date=experiment_date)

    layer_thickness_mm = process_layer_thickness(experiment_id=experiment_id, 
                                              machine_id=machine_id,
                                              experiment_date=experiment_date,
                                              layer_thickness_measured_mm=layer_thickness_measured_mm,
                                              layer_thickness_measured_point=layer_thickness_measured_point)
    
    fig, ax1 = plt.subplots()

    # Plot stress data on the left y-axis
    ax1.set_xlabel('Record Number')
    ax1.set_ylabel('Stress (MPa)', color='tab:blue')
    ax1.plot(shear_stress_MPa, label='Shear Stress (MPa)', color='tab:blue')
    ax1.plot(normal_stress_MPa, label='Normal Stress (MPa)', color='tab:cyan')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.legend(loc='upper left')

    # Create a second y-axis for displacement data
    ax2 = ax1.twinx()
    ax2.set_ylabel('Displacement (mm)', color='tab:red')
    ax2.plot(load_point_displacement_mm, label='Load Point Displacement (mm)', color='tab:red')
    ax2.plot(layer_thickness_mm, label='Layer Thickness (mm)', color='tab:orange')
    ax2.tick_params(axis='y', labelcolor='tab:red')
    ax2.legend(loc='upper right')

    fig.tight_layout()
    plt.show()

def save_reduced_experiment():
    pass

if __name__ == "__main__":
    main()


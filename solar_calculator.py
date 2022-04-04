#!/usr/bin/env python3

import os
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np
import argparse

from datetime import datetime
'''

MIGHT WANT TO CONSIDER ADDING AN OPTION FOR CALCULATING SYSTEM CURRENT FROM POWER (W) DRAW

Merge each calc_battery function into a single function? Seems nice to have them split up
just in case we want to add an input parameter for that at a later date. Just going to 
generate data and plots for all of them right now. 
'''

def calc_battery_10_hour(sol_curr, sys_curr, batt_size, sys_volt, s_time, p_eff):
    '''
    Create arrays of the battery life based on the input parameters, panel efficiencies, and 6 hours of peak solar input and 4 hours of non-peak solar input [aka 2 hours at dusk and dawn where usn agnle is not ideal.]

    EQN: previous_array_entry + (sol_curr*p_eff*scale_factor) - (sys_curr)

    input param: sol_curr, optimium solar panel output current in amps
    input param: batt_size, battery size in Amp-Hours
    input param: sys_curr, system current draw in amps
    input param: sys_volt, system voltage. Probably 12 or 24.
    input param: s_time, the sampling time.
    input param:p_eff, list of panel efficiencies to calculate over

    output param: data_dict, dictionary arrays of the data we want to plot
    '''

    time_arr = np.arange(0, s_time, 1, dtype=int)
    
    #initialize the dictionary. 
    data_dict = {}
    data_dict['t_arr'] = time_arr
    data_dict['solar_input'] = 10    
    data_dict['p_eff'] = {eff: None for eff in p_eff}
    
    # create appropriately sized arrays for calculation
    # set the first value in each array to the size of the battery. We assume we start from a fully charged battery
    for eff in p_eff:
        data_dict['p_eff'][eff] = np.zeros(s_time)
        data_dict['p_eff'][eff][0] = batt_size
    
    for eff in p_eff:
        for i in range(1, len(data_dict['p_eff'][eff])):
            
            # the total number of hours the device has been up
            up_hour = data_dict['t_arr'][i]

            # calculate hours were we don't have solar input. 
            # non-solar input hours 10 <= t <= 23
            if(up_hour%24 >= 10 and up_hour%24 <= 23):
                tot_batt = data_dict['p_eff'][eff][i-1] - sys_curr
            
            # calculate hours where we have solar input
            # solar input hours 0 <= t <= 9
            # adding simply dusk/dawn scaling factor to smooth transitions from night to day
            # solar panels work at peak efficiency even when sun angle is relatively low, so no need to go any lower [I think]
            # t = 0 or 9, scale_factor = .25
            # t = 1 or 8, scale_factor = .75
            # else, scale_factor = 1
            if(up_hour%24 >= 0 and up_hour%24 <= 9):
                if(up_hour%24 == 0 or up_hour%24 == 9):
                    scale_factor = 0.25
                elif (up_hour%24 == 1 or up_hour%24 == 8):
                    scale_factor = 0.75
                else:
                    scale_factor = 1.0
                tot_batt = data_dict['p_eff'][eff][i-1] + (sol_curr*scale_factor*float(eff)) - sys_curr
                    
            # if the battery runs greater than the battery size, set it to the battery size
            # if the battery runs negative, set it to 0.
            if tot_batt > batt_size:
                data_dict['p_eff'][eff][i] = batt_size
            elif tot_batt < 0:
                data_dict['p_eff'][eff][i] = 0
            else:
                data_dict['p_eff'][eff][i] = tot_batt
            #print(i, up_hour%24, tot_batt, data_dict[eff][i])
     
   
    return data_dict 


def calc_battery_8_hour(sol_curr, sys_curr, batt_size, sys_volt, s_time, p_eff):
    '''
    Create arrays of the battery life based on the input parameters, panel efficiencies, and 4 hours of peak solar input and 4 hours of non-peak solar input [aka 2 hours at dusk and dawn where sun angle is not ideal.]

    EQN: previous_array_entry + (sol_curr*p_eff*scale_factor) - (sys_curr)

    input param: sol_curr, optimium solar panel output current in amps
    input param: batt_size, battery size in Amp-Hours
    input param: sys_curr, system current draw in amps
    input param: sys_volt, system voltage. Probably 12 or 24.
    input param: s_time, the sampling time.
    input param:p_eff, list of panel efficiencies to calculate over

    output param: data_dict, dictionary arrays of the data we want to plot
    '''

    time_arr = np.arange(0, s_time, 1, dtype=int)
    
    #initialize the dictionary. 
    data_dict = {}
    data_dict['t_arr'] = time_arr
    data_dict['solar_input'] = 8
    data_dict['p_eff'] = {eff: None for eff in p_eff}
 
    # create appropriately sized arrays for calculation
    # set the first value in each array to the size of the battery. We assume we start from a fully charged battery
    for eff in p_eff:
        data_dict['p_eff'][eff] = np.zeros(s_time)
        data_dict['p_eff'][eff][0] = batt_size
    
    for eff in p_eff:
        for i in range(1, len(data_dict['p_eff'][eff])):
            
            # the total number of hours the device has been up
            up_hour = data_dict['t_arr'][i]

            # calculate hours were we don't have solar input. 
            # non-solar input hours 6 <= t <= 23
            if(up_hour%24 >= 8 and up_hour%24 <= 23):
                tot_batt = data_dict['p_eff'][eff][i-1] - sys_curr
            
            # calculate hours where we have solar input
            # solar input hours 0 <= t <= 7
            # adding simply dusk/dawn scaling factor to smooth transitions from night to day
            # solar panels work at peak efficiency even when sun angle is relatively low, so no need to go any lower [I think]
            # t = 0 or 7, scale_factor = .25
            # t = 1 or 6, scale_factor = .75
            # else, scale_factor = 1
            if(up_hour%24 >= 0 and up_hour%24 <= 7):
                if(up_hour%24 == 0 or up_hour%24 == 7):
                    scale_factor = 0.25
                elif (up_hour%24 == 1 or up_hour%24 == 6):
                    scale_factor = 0.75
                else:
                    scale_factor = 1.0
                tot_batt = data_dict['p_eff'][eff][i-1] + (sol_curr*scale_factor*float(eff)) - sys_curr
                    
            # if the battery runs greater than the battery size, set it to the battery size
            # if the battery runs negative, set it to 0.
            if tot_batt > batt_size:
                data_dict['p_eff'][eff][i] = batt_size
            elif tot_batt < 0:
                data_dict['p_eff'][eff][i] = 0
            else:
                data_dict['p_eff'][eff][i] = tot_batt
            #print(i, up_hour%24, tot_batt, data_dict[eff][i])
        
    return data_dict 


def calc_battery_6_hour(sol_curr, sys_curr, batt_size, sys_volt, s_time, p_eff):
    '''
    Create arrays of the battery life based on the input parameters, panel efficiencies, and 2 hours of peak solar input [scale factor = 1] and 4 hours of non peak solar input.

    EQN: previous_array_entry + (sol_curr*p_eff*scale_factor) - (sys_curr)

    input param: sol_curr, optimium solar panel output current in amps
    input param: batt_size, battery size in Amp-Hours
    input param: sys_curr, system current draw in amps
    input param: sys_volt, system voltage. Probably 12 or 24.
    input param: s_time, the sampling time.
    input param:p_eff, list of panel efficiencies to calculate over

    output param: data_dict, dictionary arrays of the data we want to plot
    '''

    time_arr = np.arange(0, s_time, 1, dtype=int)
    
    #initialize the dictionary. 
    data_dict = {}
    data_dict['t_arr'] = time_arr
    data_dict['solar_input'] = 6
    data_dict['p_eff'] = {eff: None for eff in p_eff}
    
    # create appropriately sized arrays for calculation
    # set the first value in each array to the size of the battery. We assume we start from a fully charged battery
    for eff in p_eff:
        data_dict['p_eff'][eff] = np.zeros(s_time)
        data_dict['p_eff'][eff][0] = batt_size
    
    for eff in p_eff:
        for i in range(1, len(data_dict['p_eff'][eff])):
            
            # the total number of hours the device has been up
            up_hour = data_dict['t_arr'][i]

            # calculate hours were we don't have solar input. 
            # non-solar input hours 4 <= t <= 23
            if(up_hour%24 >= 6 and up_hour%24 <= 23):
                tot_batt = data_dict['p_eff'][eff][i-1] - sys_curr
            
            # calculate hours where we have solar input
            # solar input hours 0 <= t <= 7
            # adding simply dusk/dawn scaling factor to smooth transitions from night to day
            # solar panels work at peak efficiency even when sun angle is relatively low, so no need to go any lower [I think]
            # t = 0 or 5, scale_factor = .25
            # t = 1 or 4, scale_factor = .75
            # else, scale_factor = 1
            if(up_hour%24 >= 0 and up_hour%24 <= 5):
                if(up_hour%24 == 0 or up_hour%24 == 5):
                    scale_factor = 0.25
                elif (up_hour%24 == 1 or up_hour%24 == 4):
                    scale_factor = .75
                else:
                    scale_factor = 1.0
                tot_batt = data_dict['p_eff'][eff][i-1] + (sol_curr*scale_factor*float(eff)) - sys_curr
                    
            # if the battery runs greater than the battery size, set it to the battery size
            # if the battery runs negative, set it to 0.
            if tot_batt > batt_size:
                data_dict['p_eff'][eff][i] = batt_size
            elif tot_batt < 0:
                data_dict['p_eff'][eff][i] = 0
            else:
                data_dict['p_eff'][eff][i] = tot_batt
            #print(i, up_hour%24, tot_batt, data_dict[eff][i])
        
    return data_dict 


def plot_solar_data(data, sol_curr, sys_curr, batt_size, sys_volt, max_dd, file_name):

    '''
    Plot one data set of solar data. 

    input param: data, dictionary of solar data. Does not include input parameters from system.
    input param: sol_curr, optimium solar panel output current in amps
    input param: batt_size, battery size in Amp-Hours
    input param: sys_curr, system current draw in amps
    input param: sys_volt, system voltage. Probably 12 or 24.
    input param: maxx_dd, maximum discharge depth of the battery.
    '''
   
    fig, ax = plt.subplots(1, figsize=(15,10))
    eff_str = ''

    max_discharge_line = np.full(len(data['t_arr']), max_dd*batt_size)

    for eff in data['p_eff']:
        ax.plot(data['t_arr'], data['p_eff'][eff], label = "Panel Efficiency: {}%".format(float(eff)*100))
        eff_str += str(eff).replace('.', '') + "_"

    ax.plot(data['t_arr'], max_discharge_line, color='k', label="Maximum Dishcharge Depth")    
    ax.set_xlabel("Hours Elapsed")
    ax.set_ylabel("Battery Remaining (mA)")
    ax.set_title("{} Hours Solar Input, {} AHr Battery, {}A Solar Input, {}A System Load, {}V System Voltage, {}A Maximum Battery Discharge Depth".format(data['solar_input'], batt_size, sol_curr, sys_curr, sys_volt, max_dd))
    ax.legend(loc='upper right', bbox_to_anchor=(1.23, 1.01))
    ax.grid(True) 
    
    plt.tight_layout()
    
    if file_name is None:
        plot_file = os.getcwd() + '/plots/' + "solar_plot_{}Hours_eff_{}{}SolarHours_{}.png".format(len(data['t_arr']), eff_str, data['solar_input'], datetime.now().strftime("%m-%d-%Y_%H-%M-%S"))
    else:
        plot_file = os.getcwd() + '/plots/' + "solar_plot_{}Hours_eff_{}{}SolarHours_{}.png".format(len(data['t_arr']), eff_str, data['solar_input'], file_name)


    plt.savefig(plot_file)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument('-si', '--solar_current', type=float, required=True, help='The optimum solar panel output current in Amps. Ex) 1.0. No Default. THIS VALUE MUST BE PROVIDED')
    parser.add_argument('-di', '--device_current', type=float, required=True, help='The maximum current consumed by the system in Amps. Ex) 0.5. No Default. THIS VALUE MUST BE PROVIDED.')
    parser.add_argument('-b', '--battery_size', type=float, required=True, help='The size of the battery in Amp-Hours. Ex) 50.0. No Default. THIS VALUE MUST BE PROVIDED')
    parser.add_argument('-v', '--voltage', type=float, required=True, help='The voltage provided by the solar charger to the load. Ex) 12.0. No Default. THIS VALUE MUST BE PROVIDED')
    parser.add_argument('-t', '--time_hours', type=int, help='The time in hours you would like to run. Ex.) 96', default=168)
    parser.add_argument('-dd', '--max_discharge_depth', type=float, help='The maximum discharge depth of your battery. Ex) 0.50. Default assumes LiFePO4 battery, which is generally 20%.', default=.20)
    parser.add_argument('-fn', '--plot_file_name', type=str, help='The file name of the pltos you want to save. If no name is provided, plot name will default to solar_plot_[solar hours]_m-d-Y_H-M-S.png. Recommend inputing [solar_input]_[device_current]_[battery_size]_[voltage]. Ensure there are no . characters, so conversion to milliamps may be required. Ex) 2790mA_300mA_10AHr_12V', default=None)
    parser.add_argument('-ef', '--panel_efficiencies', nargs='+', help='A list of the panel efficiencies for calculation. Minimum efficiency is 0.0, max is 1.0. Ex.) 0.1 0.3 0.9. Default is 0.0-1.0', default=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    args = parser.parse_args()

    print()
    print("Solar Panel Optimum Current Ouput: {} Amps".format(args.solar_current))
    print("Battery Size: {} Amp-Hours".format(args.battery_size))
    print("System Current Draw: {} A".format(args.device_current))
    print("System Voltage: {} V".format(args.voltage))
    print()
    print("Time Interval: {} Hours".format(args.time_hours))
    print("Panel Efficiencies: {}".format(args.panel_efficiencies))
    print()

    data_10_hour = calc_battery_10_hour(args.solar_current, args.device_current, args.battery_size, args.voltage, args.time_hours, args.panel_efficiencies)
    data_8_hour = calc_battery_8_hour(args.solar_current, args.device_current, args.battery_size, args.voltage, args.time_hours, args.panel_efficiencies)
    data_6_hour = calc_battery_6_hour(args.solar_current, args.device_current, args.battery_size, args.voltage, args.time_hours, args.panel_efficiencies)

    plot_solar_data(data_10_hour, args.solar_current, args.device_current, args.battery_size, args.voltage, args.max_discharge_depth, args.plot_file_name)
    plot_solar_data(data_8_hour, args.solar_current, args.device_current, args.battery_size, args.voltage, args.max_discharge_depth, args.plot_file_name)
    plot_solar_data(data_6_hour, args.solar_current, args.device_current, args.battery_size, args.voltage, args.max_discharge_depth, args.plot_file_name)



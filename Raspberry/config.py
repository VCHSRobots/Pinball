# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# config.py -- Configuration Data for different
# parts of the machine.
# 

from pb_log import log

config = {
    "active_nodes": [3, 4],
    "flipper_right": {
        "name": "right flipper",
        "pwm1": 255,
        "pwm2": 255,
        "delay": 50
    },
    "flipper_left": {
        "name": "left flipper",
        "pwm1": 255,
        "pwm2": 255,
        "delay": 50
    },
    "flipper_third": {
        "name": "third flipper",
        "pwm1": 255,
        "pwm2": 255,
        "delay": 50
    },
    "drop_hole_coil": {
        "name": "drop hole",
        "pwm": 100,
        "timer_on": 100
    },
    "lift_motor": {
        "name": "lift motor",
        "run_time": 4.0,
        "pwm": 255
    },
    "ball_gate_servo": {
        "name": "ball_gate_servo",
        "cycle_time": 1.5
    },
    "kicker_top": {
        "name": "kicker_top_right", 
        "pwm": 150,
        "on_time": 100,
        "rest_time": 10,
        "debounce_low": 5,
        "debounce_high": 10,
        "lamp_pwm": 255,
        "lamp_on_time": 50
    },
    "kicker_right": {
        "name": "kicker_bottom_right", 
        "pwm": 200,
        "on_time": 75,
        "rest_time": 10,
        "debounce_low": 5,
        "debounce_high": 10,
        "lamp_pwm": 255,
        "lamp_on_time": 50
    },
    "kicker_left": {
        "name": "kicker_bottom_left", 
        "pwm": 200,
        "on_time": 75,
        "rest_time": 10,
        "debounce_low": 5,
        "debounce_high": 10,
        "lamp_pwm": 255,
        "lamp_on_time": 50
    },
    "bumper_right": {
        "name": "bumper_top_right", 
        "pwm": 175,
        "on_time": 50,
        "rest_time": 10,
        "debounce_low": 5,
        "debounce_high": 10,
        "lamp_pwm": 255,
        "lamp_on_time": 50
    },
    "bumper_left": {
        "name": "bumper_top_left", 
        "pwm": 175,
        "on_time": 50,
        "rest_time": 10,
        "debounce_low": 5,
        "debounce_high": 10,
        "lamp_pwm": 255,
        "lamp_on_time": 50
    },
    "bumper_bottom": {
        "name": "bumper_bottom", 
        "pwm": 200,
        "on_time": 50,
        "rest_time": 10,
        "debounce_low": 5,
        "debounce_high": 10,
        "lamp_pwm": 255,
        "lamp_on_time": 50
    },
    "lanes": {
        "sw1_time_low": 3,
        "sw1_time_high": 5,
        "sw2_time_low": 3,
        "sw2_time_high": 5,
        "sw3_time_low": 3,
        "sw3_time_high": 5,
        "sw4_time_low": 3,
        "sw4_time_high": 5,
        "sw5_time_low": 3,
        "sw5_time_high": 5,
        "sw6_time_low": 3,
        "sw6_time_high": 5,
        "sw7_time_low": 3,
        "sw7_time_high": 5,
        "sw8_time_low": 3,
        "sw8_time_high": 5,
        "sw9_time_low": 3,
        "sw9_time_high": 5,
        "sw10_time_low": 3,
        "sw10_time_high": 5,
        "sw11_time_low": 3,
        "sw11_time_high": 5,
        "sw12_time_low": 3,
        "sw12_time_high": 5,
        "sw13_time_low": 3,
        "sw13_time_high": 5,
        "sw14_time_low": 3,
        "sw14_time_high": 5,
        "sw15_time_low": 3,
        "sw15_time_high": 5
    },
        "targets": {
        "sw1_time_low": 3,
        "sw1_time_high": 5,
        "sw2_time_low": 3,
        "sw2_time_high": 5,
        "sw3_time_low": 3,
        "sw3_time_high": 5,
        "sw4_time_low": 3,
        "sw4_time_high": 5,
        "sw5_time_low": 3,
        "sw5_time_high": 5,
        "sw6_time_low": 3,
        "sw6_time_high": 5,
        "sw7_time_low": 3,
        "sw7_time_high": 5,
        "sw8_time_low": 3,
        "sw8_time_high": 5
    }
}

def init_config():
    ''' Attemps to read the config file.'''
    pass
    
def get_active_nodes():
    return config["active_nodes"]

def get_param(module, name, default):
    '''Returns the parameter value given the module and name.  If
    the parameter doesn't exist, the default is returned.'''
    if module not in config:
        log(f"Prog Error: Module {module} not known in config.") 
        return default
    if name not in config[module]: 
        log(f"Param {name} in module {module} not known in config.")
        return default
    return config[module][name]
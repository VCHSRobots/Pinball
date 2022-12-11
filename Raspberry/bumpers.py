# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Bumpers Node handler

from pb_log import log
import hardware 
import event_manager
import config

CMD_COILS_PWM      =  20
CMD_COILS_ENABLE   =  21
CMD_COILS_TRIGGER  =  22
CMD_LAMP_ENABLE    =  23
CMD_LAMP_PWM       =  24
CMD_LAMP_SOLID     =  25
CMD_LAMP_FLASH     =  26
CMD_LAMP_MODULATE  =  27
CMD_DEBOUNCE       =  28
MASK_BUMPER_RIGHT  = 0b00000001
MASK_BUMPER_LEFT   = 0b00000010
MASK_BUMPER_BOTTOM = 0b00000100
MASK_ALL_BUMPERS   = 0b00000111

class Bumpers():
    ''' Takes care of stuff with the bumpers's node'''
    def __init__(self, gameapp, hw, sm):
        self._nodeadr = hardware.NODE_BUMPERS
        self._game = gameapp
        self._hw = hw
        self._sound = sm
        self._queue = event_manager.EventManager()

    def queue_startup_cmds(self):
        cmd = [CMD_COILS_ENABLE, MASK_ALL_BUMPERS, 0]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "disable all bumpers coils")
        cmd = [CMD_LAMP_ENABLE, MASK_ALL_BUMPERS, 0]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "disable all bumper lamps")

        pwm= config.get_param('bumper_right', 'pwm', 150)
        t_on = config.get_param('bumper_right', 'on_time', 100)
        t_off = config.get_param('bumper_right', 'rest_time', 10)
        cmd = [CMD_COILS_PWM, MASK_BUMPER_RIGHT, pwm, t_on, t_off]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "bumper_right coils_pwm")
        d_low = config.get_param('bumper_right', 'debounce_low', 5)
        d_high = config.get_param('bumper_right', 'debounce_high', 10)
        cmd = [CMD_DEBOUNCE, MASK_BUMPER_RIGHT, d_low, d_high]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "bumper_right debounce")
        lamp_pwm = config.get_param('bumper_right', 'lamp_pwm', 255)
        lamp_on_time = config.get_param('bumper_right', 'lamp_on_time', 50)
        cmd = [CMD_LAMP_PWM, MASK_BUMPER_RIGHT, lamp_pwm, lamp_on_time]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "bumper_right lamp_pwm")
  
        pwm = config.get_param('bumper_left', 'pwm', 200)
        t_on = config.get_param('bumper_left', 'on_time', 75)
        t_off = config.get_param('bumper_left', 'rest_time', 10)
        cmd = [CMD_COILS_PWM, MASK_BUMPER_LEFT, pwm, t_on, t_off]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "bumper_left coils_pwm")
        d_low = config.get_param('bumper_left', 'debounce_low', 5)
        d_high = config.get_param('bumper_left', 'debounce_high', 10)
        cmd = [CMD_DEBOUNCE, MASK_BUMPER_LEFT, d_low, d_high]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "bumper_left debounce")
        lamp_pwm = config.get_param('bumper_left', 'lamp_pwm', 255)
        lamp_on_time = config.get_param('bumper_left', 'lamp_on_time', 50)
        cmd = [CMD_LAMP_PWM, MASK_BUMPER_LEFT, lamp_pwm, lamp_on_time]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "bumper_left lamp_pwm")
        
        pwm = config.get_param('bumper_bottom', 'pwm', 200)
        t_on = config.get_param('bumper_bottom', 'on_time', 75)
        t_off = config.get_param('bumper_bottom', 'rest_time', 10)
        cmd = [CMD_COILS_PWM, MASK_BUMPER_BOTTOM, pwm, t_on, t_off]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "bumper_bottom coils_pwm")
        d_low = config.get_param('bumper_bottom', 'debounce_low', 5)
        d_high = config.get_param('bumper_bottom', 'debounce_high', 10)
        cmd = [CMD_DEBOUNCE, MASK_BUMPER_BOTTOM, d_low, d_high]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "bumper_bottom debounce")
        lamp_pwm = config.get_param('bumper_bottom', 'lamp_pwm', 255)
        lamp_on_time = config.get_param('bumper_bottom', 'lamp_on_time', 50)
        cmd = [CMD_LAMP_PWM, MASK_BUMPER_BOTTOM, lamp_pwm, lamp_on_time]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "bumper_bottom lamp_pwm")

    def process_hardware_events(self, events):
        ''' Processes hardware events that pertain to the bumpers'''
        pass

    def update(self):
        '''Processes internal events pertaining to the bumpers.'''
        events = self._queue.get_fired_events() 
        for ev in events:
            self._hw.send_command(self._nodeadr, ev['cmd'])
            if "cmd_name" in ev: name = ev['cmd_name']
            else: name = ""
            log(f"Sending Queued Command from Bumpers: {name}")

    def disable(self):
        cmd = [CMD_COILS_ENABLE, MASK_ALL_BUMPERS, 0]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Bumpers: Disabling all Bumper Coils")
        cmd = [CMD_LAMP_ENABLE, MASK_ALL_BUMPERS, 0]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Bumpers: Disabling all Bumper Lamps")

    def enable(self):
        cmd = [CMD_COILS_ENABLE, MASK_ALL_BUMPERS, 1]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Bumpers: Enabling all Bumper Coils")
        cmd = [CMD_LAMP_ENABLE, MASK_ALL_BUMPERS, 1]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Bumpers: Enabling all Bumper Lamps")
       

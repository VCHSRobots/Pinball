# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Bumpers Node handler

from pb_log import log
import hardware 
import event_manager
import config

CMD_COILS_PWM       = 20
CMD_COILS_ENABLE    = 21
CMD_COILS_TRIGGER   = 22
CMD_LAMP_ENABLE     = 23
CMD_LAMP_PWM        = 24
CMD_LAMP_SOLID      = 25
CMD_LAMP_FLASH      = 26
CMD_LAMP_MODULATE   = 27
CMD_DEBOUNCE        = 28
MASK_KICKER_TOP    = 0b00000001
MASK_KICKER_RIGHT  = 0b00000010
MASK_KICKER_LEFT   = 0b00000100
MASK_ALL_KICKERS   = 0b00000111
MASK_ALL_LAMPS     = 0b00000111

class Kickers():
    ''' Takes care of stuff with the kickers's node'''
    def __init__(self, gameapp, hw, sm):
        self._nodeadr = hardware.NODE_KICKERS
        self._game = gameapp
        self._hw = hw
        self._sound = sm
        self._queue = event_manager.EventManager()

    def queue_startup_cmds(self):
        cmd = [CMD_COILS_ENABLE, MASK_ALL_KICKERS, 0]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "disable all kickers coils")
        cmd = [CMD_LAMP_ENABLE, MASK_ALL_LAMPS, 0]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "disable all kickers lamps")

        pwm= config.get_param('kicker_top', 'pwm', 150)
        t_on = config.get_param('kicker_top', 'on_time', 100)
        t_off = config.get_param('kicker_top', 'rest_time', 10)
        cmd = [CMD_COILS_PWM, MASK_KICKER_TOP, pwm, t_on, t_off]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "kicker_top coils_pwm")
        d_low = config.get_param('kicker_top', 'debounce_low', 5)
        d_high = config.get_param('kicker_top', 'debounce_high', 10)
        cmd = [CMD_DEBOUNCE, MASK_KICKER_TOP, d_low, d_high]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "kicker_top debounce")
        lamp_pwm = config.get_param('kicker_top', 'lamp_pwm', 255)
        lamp_on_time = config.get_param('kicker_top', 'lamp_on_time', 50)
        cmd = [CMD_LAMP_PWM, MASK_KICKER_TOP, lamp_pwm, lamp_on_time]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "kicker_top lamp_pwm")
  
        pwm = config.get_param('kicker_right', 'pwm', 200)
        t_on = config.get_param('kicker_right', 'on_time', 75)
        t_off = config.get_param('kicker_right', 'rest_time', 10)
        cmd = [CMD_COILS_PWM, MASK_KICKER_RIGHT, pwm, t_on, t_off]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "kicker_right coils_pwm")
        d_low = config.get_param('kicker_right', 'debounce_low', 5)
        d_high = config.get_param('kicker_right', 'debounce_high', 10)
        cmd = [CMD_DEBOUNCE, MASK_KICKER_RIGHT, d_low, d_high]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "kicker_right debounce")
        lamp_pwm = config.get_param('kicker_right', 'lamp_pwm', 255)
        lamp_on_time = config.get_param('kicker_right', 'lamp_on_time', 50)
        cmd = [CMD_LAMP_PWM, MASK_KICKER_RIGHT, lamp_pwm, lamp_on_time]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "kicker_right lamp_pwm")
        
        pwm = config.get_param('kicker_left', 'pwm', 200)
        t_on = config.get_param('kicker_left', 'on_time', 75)
        t_off = config.get_param('kicker_left', 'rest_time', 10)
        cmd = [CMD_COILS_PWM, MASK_KICKER_LEFT, pwm, t_on, t_off]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "kicker_left coils_pwm")
        d_low = config.get_param('kicker_left', 'debounce_low', 5)
        d_high = config.get_param('kicker_left', 'debounce_high', 10)
        cmd = [CMD_DEBOUNCE, MASK_KICKER_LEFT, d_low, d_high]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "kicker_left debounce")
        lamp_pwm = config.get_param('kicker_left', 'lamp_pwm', 255)
        lamp_on_time = config.get_param('kicker_left', 'lamp_on_time', 50)
        cmd = [CMD_LAMP_PWM, MASK_KICKER_LEFT, lamp_pwm, lamp_on_time]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "kicker_left lamp_pwm")

    def process_hardware_events(self, events):
        ''' Processes hardware events that pertain to the kickers'''
        pass

    def update(self):
        '''Processes internal events pertaining to the kickers.'''
        events = self._queue.get_fired_events() 
        for ev in events:
            self._hw.send_command(self._nodeadr, ev['cmd'])
            if "cmd_name" in ev: name = ev['cmd_name']
            else: name = ""
            log(f"Sending Queued Command from Kickers: {name}")

    def disable(self):
        cmd = [CMD_COILS_ENABLE, MASK_ALL_KICKERS, 0]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Kickers: Disabling all Coils")
        cmd = [CMD_LAMP_ENABLE, MASK_ALL_LAMPS, 0]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Kickers: Disabling all Lamps")

    def enable(self):
        cmd = [CMD_COILS_ENABLE, MASK_ALL_KICKERS, 1]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Kickers: Enabling all Coils")
        cmd = [CMD_LAMP_ENABLE, MASK_ALL_LAMPS, 1]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Kickers: Enabling all Lamps")
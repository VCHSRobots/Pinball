# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Targets Node handler

from pb_log import log
import hardware 
import event_manager
import config

CMD_DEBOUNCE      =  30
CMD_DB_BANK       =  31
CMD_CLEAR_COUNTS  =  32

NSWITCHS = 8
MASK_SW1  = 0b00000001, 0
MASK_SW2  = 0b00000010, 0
MASK_SW3  = 0b00000100, 0
MASK_SW4  = 0b00001000, 0
MASK_SW5  = 0b00010000, 0
MASK_SW6  = 0b00100000, 0
MASK_SW7  = 0b01000000, 0
MASK_SW8  = 0b10000000, 0

masks = [MASK_SW1, MASK_SW2, MASK_SW3, MASK_SW4, MASK_SW5, MASK_SW6, MASK_SW7, MASK_SW8 ]

class Targets():
    ''' Takes care of stuff with the target's node'''
    def __init__(self, gameapp, hw, sm):
        self._nodeadr = hardware.NODE_TARGETS
        self._game = gameapp
        self._hw = hw
        self._sound = sm
        self._queue = event_manager.EventManager()

    def queue_startup_cmds(self):
        for i in range(NSWITCHS): 
            isw = i + 1
            mask, bank = masks[i] 
            param1 = f"sw{isw}_time_low"
            param2 = f"sw{isw}_time_high"
            t_low = config.get_param('targets', param1, 3)
            t_high = config.get_param('targets', param2, 5)
            cmd = [CMD_DB_BANK, bank, mask, t_low, t_high]
            self._hw.send_startup_cmd(self._nodeadr, cmd, f"debounce for switch {isw} tlow={t_low}, thigh={t_high}")

    def process_hardware_events(self, events):
        ''' Processes hardware events that pertain to the targets'''
        pass

    def update(self):
        '''Processes internal events pertaining to the targets.'''
        pass

 
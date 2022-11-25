import pygame
from pygame.locals import *
import time
 
class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 640, 400
        self._lasttime = time.monotonic()
        self._counter = 0
 
    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self._myfont = pygame.font.SysFont("freemono", 120, bold=True)
        fs = self._myfont.render("999999", True, (255, 255, 255), (0, 0, 0))
        self._labelsize = w, h = fs.get_width() + 16, fs.get_height() + 12
        self._labelbox = pygame.Surface(self._labelsize, 0, self._display_surf)
        self._labelbox.fill((0, 0, 0))
        r1 = pygame.Rect(1, 1, w - 2, h - 2)
        pygame.draw.rect(self._labelbox, (255, 255, 255), r1, 2)
        print("Lable box rect: ", r1)
        # print("Default font ->", pygame.font.get_default_font())
        # print("Possible Fonts:\n", pygame.font.get_fonts())
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
    def on_loop(self):
        pass
    def on_render(self):
        pass
    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            telp = time.monotonic() - self._lasttime;
            if telp > 0.1:
                self._lasttime = time.monotonic() 
                self._counter += 1
                s = f"{self._counter:06}"
                fs = self._myfont.render(s, True, (255, 255, 255), (0, 0, 0))
                self._display_surf.blit(self._labelbox, (100, 100))
                self._display_surf.blit(fs, (108, 107))
                pygame.display.update()

            self.on_loop()
            self.on_render()
        self.on_cleanup()
 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()
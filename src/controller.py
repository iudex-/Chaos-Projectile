"""
.. module:: controller
    :platform: Unix, Windows
    :synopsis: Generates events according input of various controllers connected to the game.
"""

import pygame
import events

class InputController:
    """InputController manages connected controllers and takes events generated by them sending other events to the game.
    
    :Attributes:
        - *event_manager* (events.EventManager): event manager
        - *joystick* (pygame.joystick.Joystick): game pad, tested here only with sony controller
    """

    def __init__(self, event_manager):
        #Register InputController, so it can handle events
        self.event_manager = event_manager
        self.event_manager.register_listener(self)
        #Register game pad, if any connected
        self.joystick = None
        self.joystick_count = pygame.joystick.get_count()
        if self.joystick_count > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def notify(self, event):
        if isinstance(event, events.TickEvent):
            #Every CPU-tick handle input events
            for event in pygame.event.get():
                if event.type == pygame.VIDEORESIZE:
                    resize_ev = events.ResizeWindowEvent(event.w, event.h)
                    self.event_manager.post(resize_ev)
                if event.type == pygame.QUIT:
                    quit_ev = events.QuitEvent()
                    self.event_manager.post(quit_ev)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit_ev = events.QuitEvent()
                        self.event_manager.post(quit_ev)

                if not self.joystick:
                    #Handle events generated by keyboard
                    if event.type == pygame.KEYDOWN:
                        key_ev = events.KeyPressed(event.key)
                        self.event_manager.post(key_ev)
                    if event.type == pygame.KEYUP:
                        key_ev = events.KeyReleased(event.key)
                        self.event_manager.post(key_ev)
                    #Handle events generated by mouse    
                    if event.type == pygame.MOUSEMOTION:
                        direction_X, direction_Y = pygame.mouse.get_pos()
                        mouse_ev = events.MouseMoved(direction_X, 
                                                     direction_Y)
                        self.event_manager.post(mouse_ev)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        attack_request_ev = events.PlayerAttackRequest()
                        self.event_manager.post(attack_request_ev)

                #Handle events generated by game pad
                if self.joystick:
                    '''
                    XBox game pad 2. axis: X 3, Y 4
                    Sony game pad 2. axis: X 3, Y 2
                    '''
                    horiz_axis_pos = self.joystick.get_axis(3)
                    vert_axis_pos = self.joystick.get_axis(2)
                    #Game pad events will be sent every tick
                    #Get second axis values and send this as an event
                    axis_ev = events.AxisMoved(horiz_axis_pos,
                                               vert_axis_pos)
                    self.event_manager.post(axis_ev)
                    if self.joystick.get_hat(0):
                        #Get hat values and send this as an event
                        hat_x, hat_y = self.joystick.get_hat(0)
                        hat_ev = events.HatMoved(hat_x, hat_y)
                        self.event_manager.post(hat_ev)
                    if event.type == pygame.JOYBUTTONDOWN:
                        #Check if R1 (on Sony controller) button pressed
                        if self.joystick.get_button(7):
                            attack_request_ev = events.PlayerAttackRequest()
                            self.event_manager.post(attack_request_ev)

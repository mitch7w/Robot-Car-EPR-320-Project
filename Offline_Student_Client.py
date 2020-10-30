import pygame
import numpy as np
import math
import serial
import socket
import selectors
import types
import random
from datetime import datetime
import time
from scipy import signal

""" Offline Client v1.9
"""

random.seed()

WHITE = (255,255,255)
RED_up = (255,0,0)
RED_low = (230,50,50)
GREEN_up = (0,255,0)
GREEN_low = (100,200,100)
BLUE_up = (0,0,255)
BLUE_low = (50,50,230)
BLACK = (1,1,1)

COLOR_LIST = [RED_up,GREEN_up,BLUE_up]

  
class pygameView(object):
 
   
    def __init__(self, width=800, height=600, fps=120):
        """Setup GUI
        """
        pygame.mixer.pre_init(44100, -16, 1) # 44.1kHz, 16-bit signed, stereo
        pygame.init()
        pygame.display.set_caption("Press ESC to quit.")
        
         
        self.width = width
        self.height = height
         
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()  
        # dark blackground
        self.background.fill((25, 35, 45))
 
        self.act_surface = self.screen
        self.act_rgb = 255, 0, 0
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.mouse = (0, 0)
        self.font = pygame.font.SysFont('mono', 24, bold=True)
        
        self.group_number = 0
        
        self.subsys = 3
        self.qtp1_state = 0
        self.qtp2_state = 0
        self.qtp3_state = 0
        self.qtp4_state = 0
        self.qtp5_state = 0
        self.qtp_tx = False
        self.counter = 0
        self.test_time = 0
        self.ls = [0,1,2,3,4]
        self.direction = True
        
        self.qtp1_pushed = False
        self.qtp2_pushed = False
        self.qtp3_pushed = False
        self.qtp4_pushed = False
        self.qtp5_pushed = False
        self.qtp_color = WHITE
        self.race_color = GREEN_up
        self.line_y = 0
        self.V_op = 50
        self.Bat = 100
        self.rho = 0
        self.rho_color = 'G'
        self.speed = 0
        self.f = 0
        
        self.log_file = log("Client_log.txt")
        self.sound = pygame.sndarray
        self.playing = False
        
        
        marv_wheel_radius = 22 # radius of warv wheel in mm
        marv_axis_length = 100 # length of marv axis from center of each wheel in mm
        marv_max_rpm = 60 # max rotational speed of marv wheel in rpm;
        marv_sensor_distance = 100 # distance of sensor from centre of axis to centre of sensor array
        marv_sensor_array_length = 100 # length of marv sensor array
        DropIns =  [1, 1, 0] # Sensor, Motor, SC3 drop-in enable (Drop in enabled if true)
        self.marv = MARV(self.group_number, marv_wheel_radius, marv_axis_length, marv_max_rpm, marv_sensor_distance, marv_sensor_array_length, DropIns)
         
    def draw_static(self):
 
        self.act_surface = self.background
 
 
    def set_draw_dynamic(self):
 
        self.act_surface = self.screen
 
 
    def set_color(self, rgb):
 
        self.act_rgb = rgb
 
         
    def draw_surf(self, surface,x,y):
        """
        """     
        self.act_surface.blit(surface, (x, y))
        
    def draw_text(self, text,x,y,color):
        """Write text at x,y with color
        """
        self.background.fill((25, 35, 45),(0,0,self.width/2,25))
        self.draw_static()
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, color)
        rect = surface.get_rect()
        self.background.fill((25, 35, 45),(x,y,rect.width,rect.height))
        self.act_surface.blit(surface, (x,y))
        self.set_draw_dynamic()
        pygame.display.update((x,y,rect.width,rect.height))
        
    def draw_status(self, text,color):
        """Write text at top with color
        """
        self.background.fill((25, 35, 45),(0,0,self.width/2,25))
        self.draw_static()
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, color)
        self.act_surface.blit(surface, (0,0))
        self.screen.blit(self.background, (0, 0), (0,0,self.width/2,25))#
        self.set_draw_dynamic()
        pygame.display.update((0,0,self.width/2,25))
        
    def get_plot_data(self,canvas):  
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()        
        return (raw_data,size)
    
    def control_validity(self,control_byte):
        library = [0,1,16,80,96,97,112,113,145,146,161,162,163,177,178,208,228]
        if control_byte in library: 
            return True
        else: 
            return False        
        
    def play_sound(self,sample_wave):
        """Play the given NumPy array, as a sound, for ms milliseconds."""
        self.sound = pygame.sndarray.make_sound(sample_wave)
        self.sound.play(-1)
        self.playing = True
        
        
    def stop_sound(self): 
        self.playing = False
        self.sound.stop()
        
    def qtp1(self,com_bot,boxes,lines,buttons):
        if self.subsys == 0:
            if (self.qtp1_state == 0):
                self.draw_status("QTP1 unimplemented. ",(176,230,134))
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP1: " + str(self.subsys)+'\n')
                self.qtp1_state = 1
            elif (self.qtp1_state == 1):
                self.qtp1_state = 2
            else:
                self.draw_status("Waiting for QTP selection. ",(176,230,134))
                boxes.default_color()
                lines.default_color()
                self.qtp1_state = 0
                buttons[3].clear_pushed()#
                self.qtp_tx = True
                self.qtp1_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP1: " + str(self.subsys)+'\n')
        
        elif self.subsys == 1:
            if (self.qtp1_state == 0):
                self.draw_status("QTP unimplemented. ",(176,230,134))
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP1: " + str(self.subsys)+'\n')
                self.qtp1_state = 1
            elif (self.qtp1_state == 1):
                self.qtp1_state = 2
            else:
                self.draw_status("Waiting for QTP selection. ",(176,230,134))
                boxes.default_color()
                lines.default_color()
                self.qtp1_state = 0
                buttons[3].clear_pushed()#
                self.qtp_tx = True
                self.qtp1_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP1: " + str(self.subsys)+'\n')
        
        elif self.subsys == 2:
            self.draw_status("QTP unimplemented. ",(176,230,134))
            if (self.qtp1_state == 0):
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP1: " + str(self.subsys)+'\n')
                self.qtp1_state = 1
            elif (self.qtp1_state == 1):
                self.qtp1_state = 2
            else:
                self.draw_status("Waiting for QTP selection. ",(176,230,134))
                boxes.default_color()
                lines.default_color()
                self.qtp1_state = 0
                buttons[3].clear_pushed()#
                self.qtp_tx = True
                self.qtp1_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP1: " + str(self.subsys)+'\n')
        else:
            self.qtp1_pushed = False
    
    def qtp2(self,com_bot,boxes,lines,buttons):
        if self.subsys == 0:
            """ QTP2 for Sensor. Sends button press (CAL command). Then cycles 
            through colours for 90 seconds. Reads colour after CAL and transmits 
            end.
            """
            if (self.qtp2_state == 0):
                self.draw_status("Running QTP 2. ",(176,230,134))
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Subsystem: " + str(self.subsys)+'\n')
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP2: " + str(self.subsys)+'\n')
                if self.race_color == GREEN_up:
                    race_colour = ord('G')
                elif  self.race_color == RED_up:
                    race_colour = ord('R')
                elif  self.race_color == BLUE_up:
                    race_colour = ord('B')
                else:
                    race_colour = ord('G')
                qtp2_data = [16,1,race_colour,0]
                com_bot.send_ser_data(qtp2_data)
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp2_data)+'\n')
                self.qtp_tx = False
                self.test_time = 0
                self.clock.tick()                       
                self.qtp2_state = 1
                
            elif (self.qtp2_state == 1):
                # Calibrate white                
                boxes.change_color(WHITE)
                lines.change_color(WHITE)
                self.test_time += self.clock.tick()
                if self.test_time > 18000:
                    self.qtp2_state = 2
                    self.qtp_tx = True
                    
            elif (self.qtp2_state == 2):
                # Calibrate red
                # print('Display red')
                boxes.change_color(RED_up)
                lines.change_color(RED_up)
                self.test_time += self.clock.tick()
                if self.test_time > 36000:
                    self.qtp2_state = 3
                    self.qtp_tx = True
                    
            elif (self.qtp2_state == 3):
                # Calibrate green
                # print('Display green')
                boxes.change_color(GREEN_up)
                lines.change_color(GREEN_up)
                self.test_time += self.clock.tick()
                if self.test_time > 54000:
                    self.qtp2_state = 4
                    self.qtp_tx = True
                    
            elif (self.qtp2_state == 4):
                # Calibrate blue
                # print('Display blue')
                boxes.change_color(BLUE_up)
                lines.change_color(BLUE_up)
                self.test_time += self.clock.tick()
                if self.test_time > 72000:
                    self.qtp2_state = 5
                    self.qtp_tx = True
                    
            elif (self.qtp2_state == 5):
                # Calibrate black
                # print('Display black')
                boxes.change_color(BLACK)
                lines.change_color(BLACK)
                self.test_time += self.clock.tick()
                if self.test_time > 90000:
                    self.qtp2_state = 6
                    self.qtp_tx = True
                    self.test_time = 0
                    boxes.default_color()
                    lines.default_color()
                    
            elif (self.qtp2_state == 6):                
                qtp2_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                lines.rect.centery = boxes.rect.centery
                if qtp2_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp2_get)+'\n')
                    com_bot.send_ser_data(qtp2_get)
                    if (qtp2_get[0] == 112):
                        self.clock.tick()
                        self.test_time = 0
                        boxes.change_color(WHITE)
                        lines.default_color()
                        self.ls = [0,1,2]
                        random.shuffle(self.ls)
                        self.qtp2_state = 7
                        self.qtp_tx = True
                        self.counter = 0
                elif self.test_time > 60000:
                    self.clock.tick()
                    self.test_time = 0
                    boxes.change_color(WHITE)
                    lines.change_color(GREEN_up)                    
                    self.qtp_color = GREEN_up
                    self.ls = [0,1,2]
                    random.shuffle(self.ls)
                    self.qtp2_state = 7
                    self.qtp_tx = True
                    self.counter = 0
                    
            elif (self.qtp2_state == 7):
                if (self.qtp_tx == True):
                    qtp2_data = [97,0,0,0]
                    com_bot.send_ser_data(qtp2_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp2_data)+'\n')
                    self.qtp_tx = False                    
                qtp2_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp2_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp2_get)+'\n')
                    com_bot.send_ser_data(qtp2_get)
                    if qtp2_get[0] == 113:
                        self.qtp_tx = True                        
                        self.counter += 1
                        if self.qtp_color == RED_up:
                            col = ord('R')
                        elif self.qtp_color == GREEN_up:
                            col = ord('G')
                        elif self.qtp_color == BLUE_up:
                            col = ord('B')
                        else:
                            col = ord('G')
                        self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " RefCol: " + str(col) +'\n')
                        self.qtp2_state = 8
                elif (self.test_time < 60000):
                    pass
                else:                            
                    self.qtp2_state = 8
                    self.qtp_tx = True
                    
            elif (self.qtp2_state == 8):
                if (self.qtp_tx == True):
                    qtp2_data = [1,0,0,0]
                    com_bot.send_ser_data(qtp2_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp2_data)+'\n')
                    self.qtp_tx = False
                
                self.qtp2_state = 9
                self.qtp_tx = True
            else:
                self.draw_status("Wating for QTP selection.",(176,230,134))
                boxes.default_color()
                lines.default_color()
                self.qtp2_state = 0
                buttons[4].clear_pushed()#
                self.qtp_tx = True
                self.qtp2_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP2: " + str(self.subsys)+'\n')
                
        elif self.subsys == 1:
            """ QTP 2 for SC3 subsystem.
            """
            if (self.qtp2_state == 0):
                self.draw_status("Running QTP 2. ",(176,230,134))
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Subsystem: " + str(self.subsys)+'\n')
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP2: " + str(self.subsys)+'\n')
                qtp2_data = [0,0,0,0]
                com_bot.send_ser_data(qtp2_data)
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp2_data)+'\n')
                self.qtp_tx = False
                self.test_time = 0
                self.clock.tick()
                self.qtp2_state = 1
                self.race_color = WHITE
                
            elif (self.qtp2_state == 1):
                qtp2_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp2_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp2_get)+'\n')
                    com_bot.send_ser_data(qtp2_get)
                    if (qtp2_get[0] == 16):
                        if (qtp2_get[1] == 1):
                            self.qtp2_state = 3
                            self.qtp_tx = True
                            self.counter = 0
                            selected_color = chr(qtp2_get[2])
                            if selected_color == 'R':
                                self.race_color = RED_up
                            elif selected_color == 'G':
                                self.race_color = GREEN_up
                            elif selected_color == 'B':
                                self.race_color = BLUE_up
                            else:
                                self.race_color = GREEN_up
                            lines.change_color(self.race_color)
                        else:
                            pass
                elif (self.test_time < 30000):
                    pass
                else:
                    self.qtp3_state = 3
                    self.qtp_tx = True
                    
            elif (self.qtp2_state == 3):
                if (self.qtp_tx == True):
                    qtp2_data = [112,0,0,0]
                    com_bot.send_ser_data(qtp2_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp2_data)+'\n')
                    self.qtp_tx = True
                    self.qtp2_state = 4
                    
            elif (self.qtp2_state == 4):
                if (self.qtp_tx == True):
                    qtp2_data = [96,self.V_op,self.V_op,0] #TODO set V_op
                    com_bot.send_ser_data(qtp2_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp2_data)+'\n')
                    self.qtp_tx = True
                    self.qtp2_state = 5
                    self.test_time = 0
                    self.clock.tick()
                    
            elif (self.qtp2_state == 5):
                if (self.qtp_tx == True):
                    qtp2_data = [97,self.Bat,0,0] # TODO battery
                    com_bot.send_ser_data(qtp2_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp2_data)+'\n')
                    self.qtp_tx = True
                    self.qtp2_state = 6
                    self.test_time = 0
                    self.clock.tick()
                    
            elif (self.qtp2_state == 6):
                if (self.qtp_tx == True):
                    qtp2_data = [113,0,0,0]
                    com_bot.send_ser_data(qtp2_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp2_data)+'\n')
                    self.qtp_tx = True
                    self.qtp2_state = 7
                    self.test_time = 0
                    self.clock.tick()
                    
            elif (self.qtp2_state == 7):
                qtp2_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp2_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp2_get)+'\n')
                    com_bot.send_ser_data(qtp2_get)
                    if (qtp2_get[0] == 80):
                        if (qtp2_get[1] == 1):
                            self.qtp2_state = 8
                            self.qtp_tx = True
                            self.counter = 0
                            selected_color = chr(qtp2_get[2])
                            if selected_color == 'R':
                                self.race_color = RED_up
                            elif selected_color == 'G':
                                self.race_color = GREEN_up
                            elif selected_color == 'B':
                                self.race_color = BLUE_up
                            else:
                                self.race_color = GREEN_up
                            lines.change_color(self.race_color)
                        else:
                            self.qtp2_state = 5
                            self.qtp_tx = True
                elif (self.test_time < 30000):
                    pass
                else:
                    self.qtp3_state = 8
                    self.qtp_tx = True
                    
            else:
                qtp2_data = [1,0,0,0]
                com_bot.send_ser_data(qtp2_data)
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp2_data)+'\n')
                self.draw_status("Waiting for QTP selection. ",(176,230,134))
                boxes.default_color()
                lines.default_color()
                self.qtp2_state = 0
                buttons[4].clear_pushed()
                self.qtp_tx = True
                self.qtp2_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP2: " + str(self.subsys)+'\n')
                
        elif self.subsys == 2: # TODO
            """ QTP 2 for MDPS subsystem.
            """
            if (self.qtp2_state == 0):
                self.draw_status("Running QTP 2. ",(176,230,134))
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Subsystem: " + str(self.subsys)+'\n')
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP2: " + str(self.subsys)+'\n')
                self.qtp_tx = True
                self.test_time = 0
                self.clock.tick()
                self.qtp2_state = 1
                
            elif (self.qtp2_state == 1):
                if (self.qtp_tx == True):
                    qtp2_data = [112,0,0,0]
                    com_bot.send_ser_data(qtp2_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp2_data)+'\n')
                    self.qtp_tx = False
                    self.qtp2_state = 2
                    self.test_time = 0
                    self.clock.tick()
            
            elif (self.qtp2_state == 2):
                qtp2_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp2_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp2_get)+'\n')
                    com_bot.send_ser_data(qtp2_get)
                    if qtp2_get[0] == 96:
                        self.qtp_tx = True                        
                        self.V_op = qtp2_get[1]
                        self.qtp2_state = 3
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp2_state = 3
                    self.qtp_tx = True
            
            elif (self.qtp2_state == 3):
                qtp2_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp2_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp2_get)+'\n')
                    com_bot.send_ser_data(qtp2_get)
                    if qtp2_get[0] == 97:
                        self.qtp_tx = True
                        self.qtp2_state = 4
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp2_state = 4
                    self.qtp_tx = True
            
            elif (self.qtp2_state == 4):
                if (self.qtp_tx == True):
                    qtp2_data = [146,0,0,0]
                    com_bot.send_ser_data(qtp2_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp2_data)+'\n')
                    self.qtp_tx = False
                    self.qtp2_state = 5
                    self.test_time = 0
                    self.clock.tick()
            
            elif (self.qtp2_state == 5):
                qtp2_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp2_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp2_get)+'\n')
                    com_bot.send_ser_data(qtp2_get)
                    if qtp2_get[0] == 161:
                        self.qtp_tx = True
                        self.qtp2_state = 6
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp2_state = 6
                    self.qtp_tx = True
            
            elif (self.qtp2_state == 6):
                qtp2_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp2_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp2_get)+'\n')
                    com_bot.send_ser_data(qtp2_get)
                    if qtp2_get[0] == 162:
                        self.qtp_tx = True
                        self.qtp2_state = 7
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp2_state = 7
                    self.qtp_tx = True
            
            elif (self.qtp2_state == 7):
                qtp2_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp2_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp2_get)+'\n')
                    com_bot.send_ser_data(qtp2_get)
                    if qtp2_get[0] == 163:
                        self.qtp_tx = True
                        self.qtp2_state = 8
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp2_state = 8
                    self.qtp_tx = True
            
            else:
                qtp2_data = [1,0,0,0]
                com_bot.send_ser_data(qtp2_data)
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp2_data)+'\n')
                self.draw_status("Waiting for QTP selection. ",(176,230,134))
                boxes.default_color()
                lines.default_color()
                self.qtp2_state = 0
                buttons[4].clear_pushed()#
                self.qtp_tx = True
                self.qtp2_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP2: " + str(self.subsys)+'\n')
        else:
            self.draw_status("Waiting for QTP selection. ",(176,230,134))
            boxes.default_color()
            lines.default_color()
            self.qtp2_state = 0
            buttons[4].clear_pushed()#
            self.qtp_tx = True
            self.qtp2_pushed = False
    
    def qtp3(self,com_bot,boxes,lines,buttons,graphs):        
        if self.subsys == 0:
            """ QTP 3 for Sensor subsystem.
            """
            if (self.qtp3_state == 0):
                self.draw_status("Running QTP 3. ",(176,230,134))
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Subsystem: " + str(self.subsys)+'\n')
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP3: " + str(self.subsys)+'\n')
                self.qtp_tx = True
                self.test_time = 0
                self.clock.tick()                       
                self.qtp3_state = 1
                lines.rect.centery = boxes.rect.centery
                
            elif (self.qtp3_state == 1):
                if (self.qtp_tx == True):
                    qtp3_data = [163,0,0,0]
                    com_bot.send_ser_data(qtp3_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp3_data)+'\n')
                    self.qtp_tx = False
                    self.clock.tick()
                    self.test_time = 0
                    boxes.change_color(WHITE)
                    lines.change_color(RED_up)
                    
                    self.qtp_color = RED_up
                    self.qtp3_state = 2
                    
            elif (self.qtp3_state == 2):
                qtp3_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp3_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp3_get)+'\n')
                    com_bot.send_ser_data(qtp3_get)
                    if (qtp3_get[0] == 177):                        
                        self.qtp3_state = 3
                        self.qtp_tx = True
                        self.counter = 0
                elif (self.test_time < 5000):
                    pass
                else:
                    self.qtp3_state = 3
                    self.qtp_tx = True
                    
            elif (self.qtp3_state == 3):
                if (self.qtp_tx == True):
                    qtp3_data = [163,0,0,0]
                    com_bot.send_ser_data(qtp3_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp3_data)+'\n')
                    self.qtp_tx = False
                    self.clock.tick()
                    self.test_time = 0
                    boxes.change_color(WHITE)
                    lines.change_color(GREEN_up)
                    self.qtp_color = GREEN_up
                    self.qtp3_state = 4
                    
            elif (self.qtp3_state == 4):
                qtp3_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp3_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp3_get)+'\n')
                    com_bot.send_ser_data(qtp3_get)
                    if (qtp3_get[0] == 177):                        
                        self.qtp3_state = 5
                        self.qtp_tx = True
                        self.counter = 0
                elif (self.test_time < 5000):
                    pass
                else:
                    self.qtp3_state = 5
                    self.qtp_tx = True
                    
            elif (self.qtp3_state == 5):
                if (self.qtp_tx == True):
                    qtp3_data = [163,0,0,0]
                    com_bot.send_ser_data(qtp3_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp3_data)+'\n')
                    self.qtp_tx = False
                    self.clock.tick()
                    self.test_time = 0
                    boxes.change_color(WHITE)
                    lines.change_color(BLUE_up)
                    self.qtp_color = BLUE_up
                    self.qtp3_state = 6
                    
            elif (self.qtp3_state == 6):
                qtp3_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp3_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp3_get)+'\n')
                    com_bot.send_ser_data(qtp3_get)
                    if (qtp3_get[0] == 177):                        
                        self.qtp3_state = 7
                        self.qtp_tx = True
                        self.counter = 0
                elif (self.test_time < 5000):
                    pass
                else:
                    self.qtp3_state = 7
                    self.qtp_tx = True
                    
            elif (self.qtp3_state == 7):
                if (self.qtp_tx == True):
                    qtp3_data = [163,0,0,0]
                    com_bot.send_ser_data(qtp3_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp3_data)+'\n')
                    self.qtp_tx = False
                    self.clock.tick()
                    self.test_time = 0
                    boxes.change_color(WHITE)
                    lines.change_color(WHITE)
                    self.qtp_color = WHITE
                    self.qtp3_state = 8
                    
            elif (self.qtp3_state == 8):
                qtp3_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp3_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp3_get)+'\n')
                    com_bot.send_ser_data(qtp3_get)
                    if (qtp3_get[0] == 177):                        
                        self.qtp3_state = 9
                        self.qtp_tx = True
                        self.counter = 0
                elif (self.test_time < 5000):
                    pass
                else:
                    self.qtp3_state = 9
                    self.qtp_tx = True
                    
            elif (self.qtp3_state == 9):
                if (self.qtp_tx == True):
                    qtp3_data = [163,0,0,0]
                    com_bot.send_ser_data(qtp3_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp3_data)+'\n')
                    self.qtp_tx = False
                    self.clock.tick()
                    self.test_time = 0
                    boxes.change_color(WHITE)
                    lines.change_color(BLACK)
                    self.qtp_color = BLACK
                    self.qtp3_state = 10
                    
            elif (self.qtp3_state == 10):
                qtp3_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp3_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp3_get)+'\n')
                    com_bot.send_ser_data(qtp3_get)
                    if (qtp3_get[0] == 177):                        
                        self.qtp3_state = 11
                        self.qtp_tx = True
                        self.counter = 0
                elif (self.test_time < 5000):
                    pass
                else:
                    self.qtp3_state = 11
                    self.qtp_tx = True
                    
            elif (self.qtp3_state == 11):
                if (self.qtp_tx == True):
                    qtp3_data = [163,0,0,0]
                    com_bot.send_ser_data(qtp3_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp3_data)+'\n')
                    self.qtp_tx = False
                    self.clock.tick()
                    self.test_time = 0
                    boxes.change_color(BLACK)
                    lines.change_color(BLACK)
                    self.qtp_color = BLACK
                    self.qtp3_state = 12
                    
            elif (self.qtp3_state == 12):
                qtp3_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp3_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp3_get)+'\n')
                    com_bot.send_ser_data(qtp3_get)
                    if (qtp3_get[0] == 178):                        
                        self.qtp3_state = 13
                        self.qtp_tx = True
                        self.counter = 0
                    elif (qtp3_get[0] == 177):                        
                        self.qtp3_state = 11
                        self.qtp_tx = True
                        self.counter = 0
                elif (self.test_time < 5000):
                    pass
                else:
                    self.qtp3_state = 13
                    self.qtp_tx = True
            else:
                qtp3_data = [1,0,0,0]
                com_bot.send_ser_data(qtp3_data)
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp3_data)+'\n')
                self.draw_status("Waiting for QTP selection. ",(176,230,134))
                boxes.default_color()
                lines.default_color()
                self.qtp3_state = 0
                buttons[5].clear_pushed()#
                self.qtp_tx = True
                self.qtp3_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP3: " + str(self.subsys)+'\n')
                
        elif self.subsys == 1:
            """ QTP 3 for SC3 subsystem.
            """
            if (self.qtp3_state == 0):
                self.draw_status("Running QTP 3. ",(176,230,134))
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Subsystem: " + str(self.subsys)+'\n')
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP3: " + str(self.subsys)+'\n')
                self.qtp_tx = True
                self.test_time = 0
                self.clock.tick()                       
                self.qtp3_state = 1
                self.counter = 0                
                
            elif (self.qtp3_state == 1):                
                self.marv.Zz_MARV_HUB()
                self.counter += 1
                self.rho = int(self.marv.sens_rho)
                self.qtp3_state = 2
            
            elif (self.qtp3_state == 2):
                if (self.qtp_tx == True):
                    rho = abs(self.rho)
                    if self.rho != 0:
                        sign = int(self.rho/rho+1)
                    else:
                        sign = 2
                    qtp3_data = [177,rho,ord(self.rho_color),sign]
                    com_bot.send_ser_data(qtp3_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp3_data)+'\n')
                    self.qtp_tx = False
                    self.clock.tick()
                    self.test_time = 0
                    self.qtp3_state = 3
            
            elif (self.qtp3_state == 3):
                qtp3_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()                
                if qtp3_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp3_get)+'\n')
                    com_bot.send_ser_data(qtp3_get)
                    if (qtp3_get[0] == 145):
                        self.clock.tick()
                        self.test_time = 0
                        self.qtp3_state = 4
                        self.qtp_tx = True                        
                elif (self.test_time < 5000):
                    pass
                else:
                    self.clock.tick()
                    self.test_time = 0                    
                    self.qtp3_state = 4
                    self.qtp_tx = True
            
            elif (self.qtp3_state == 4):
                qtp3_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()                
                if qtp3_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp3_get)+'\n')
                    com_bot.send_ser_data(qtp3_get)
                    if (qtp3_get[0] == 146):
                        self.clock.tick()
                        self.test_time = 0
                        self.qtp3_state = 5
                        self.qtp_tx = True
                        self.marv.sc3_set_point[0] = qtp3_get[1]
                        self.marv.sc3_set_point[1] = qtp3_get[2]
                elif (self.test_time < 200):
                    pass
                else:
                    self.clock.tick()
                    self.test_time = 0                    
                    self.qtp3_state = 5
                    self.qtp_tx = True
            
            elif (self.qtp3_state == 5):
                if (self.counter >= 1000):
                    self.qtp3_state = 6
                    self.qtp_tx = True                    
                else:
                    self.qtp3_state = 1
                    self.qtp_tx = True
                    x3 = self.marv.y[0,:]
                    y3 = self.marv.y[1,:]
                    graphs[1].update(x3,y3,(120, 0, 0))
            
            else:
                qtp3_data = [1,0,0,0]
                com_bot.send_ser_data(qtp3_data)
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp3_data)+'\n')
                self.draw_status("Waiting for QTP selection. ",(176,230,134))
                err = self.marv.find_error()
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " RefErr: " + str(err)+' mm\n')
                boxes.default_color()
                lines.default_color()
                self.qtp3_state = 0
                buttons[5].clear_pushed()#
                self.qtp_tx = True
                self.qtp3_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP3: " + str(self.subsys)+'\n')
                
        elif self.subsys == 2:
            """ QTP 3 for MDPS subsystem.
            """
            if (self.qtp3_state == 0):
                self.draw_status("QTP unimplemented. ",(176,230,134))
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Subsystem: " + str(self.subsys)+'\n')
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP3: " + str(self.subsys)+'\n')
                self.qtp_tx = True
                self.test_time = 0
                self.clock.tick()
                self.qtp3_state = 1
                
            elif (self.qtp3_state == 1):                
                self.qtp3_state = 2                    
                    
            else:
                self.draw_status("Waiting for QTP selection. ",(176,230,134))
                boxes.default_color()
                lines.default_color()
                self.qtp3_state = 0
                buttons[5].clear_pushed()#
                self.qtp_tx = True
                self.qtp3_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP3: " + str(self.subsys)+'\n')
        else:
            self.qtp3_pushed = False
    
    def qtp4(self,com_bot,boxes,lines,buttons):
        if self.subsys == 0:
            """ QTP4 for Sensor subsystem
            """
            if (self.qtp4_state == 0):
                self.draw_status("Running QTP 4. ",(176,230,134))
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Subsystem: " + str(self.subsys)+'\n')
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP4: " + str(self.subsys)+'\n')            
                self.qtp_tx = True
                self.test_time = 0
                self.clock.tick()                       
                self.qtp4_state = 1
                boxes.change_color(WHITE)
                lines.change_color(self.race_color)
                self.counter = 0
                lines.rect.centery = boxes.rect.centery
                
            elif (self.qtp4_state == 1):                
                if (self.direction):                    
                    if (lines.rect.top > boxes.rect.top):
                        lines.change_pos(-int(boxes.rect.h/50))
                        # print('Going up?', 'LT=',lines.rect.top,'RT',boxes.rect.top)
                    else:
                        self.direction = not self.direction
                else:                    
                    if (lines.rect.bottom < boxes.rect.bottom):
                        # print('Going down?', 'LB=',lines.rect.bottom,'RB',boxes.rect.bottom)
                        lines.change_pos(int(boxes.rect.h/50))
                        # print('Going up')
                    else:
                        self.direction = not self.direction
                self.counter += 1
                self.qtp4_state = 2
                # print('Test. Line position =', lines.rect.centery)
                        
            elif (self.qtp4_state == 2):
                if (self.qtp_tx == True):
                    qtp4_data = [163,0,0,0]
                    com_bot.send_ser_data(qtp4_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp4_data)+'\n')
                    self.qtp_tx = False
                    self.clock.tick()
                    self.test_time = 0
                    self.qtp4_state = 3
                    
            elif (self.qtp4_state == 3):
                qtp4_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()                
                if qtp4_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp4_get)+'\n')
                    com_bot.send_ser_data(qtp4_get)
                    if (qtp4_get[0] == 177):
                        rho = int(100*((lines.rect.centery-boxes.rect.centery)/boxes.rect.h))
                        self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " RefOff: " + str(rho) +'\n')
                        self.qtp4_state = 4
                        self.qtp_tx = True                        
                elif (self.test_time < 200):
                    pass
                else:                    
                    self.qtp4_state = 4
                    self.qtp_tx = True
                    
            elif (self.qtp4_state == 4):
                if (self.counter > 150):
                    self.qtp4_state = 5
                else:
                    self.qtp4_state = 1
                    
            else:
                self.draw_status("Waiting for QTP selection. ",(176,230,134))
                qtp4_data = [1,0,0,0]
                com_bot.send_ser_data(qtp4_data)
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp4_data)+'\n')
                boxes.default_color()
                lines.default_color()
                lines.rect.centery = boxes.rect.centery
                self.qtp4_state = 0
                buttons[6].clear_pushed()#
                self.qtp_tx = True
                self.qtp4_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP4: " + str(self.subsys)+'\n')
                
        elif self.subsys == 1:
            """ QTP4 for SC3 subsystem
            """
            if (self.qtp4_state == 0):
                self.draw_status("Running QTP 4. ",(176,230,134))
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Subsystem: " + str(self.subsys)+'\n')
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP4: " + str(self.subsys)+'\n')
                self.qtp_tx = True
                self.test_time = 0
                self.clock.tick()                       
                self.qtp4_state = 1
                boxes.change_color(WHITE)
                lines.change_color(self.race_color)
                self.counter = 0
                self.rho = 0
                self.Bat = 100
                self.speed = 60   
                self.counter = 0
                self.direction = True
                
            elif (self.qtp4_state == 1):
                if (self.qtp_tx == True):
                    self.counter += 1
                    qtp4_data = [161,self.Bat,0,0]
                    com_bot.send_ser_data(qtp4_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp4_data)+'\n')
                    self.qtp_tx = True
                    self.clock.tick()
                    self.test_time = 0
                    self.qtp4_state = 2
            
            elif (self.qtp4_state == 2):
                if (self.qtp_tx == True):
                    pwm = int(50*self.speed/self.V_op)
                    qtp4_data = [162,pwm,pwm,0]
                    com_bot.send_ser_data(qtp4_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp4_data)+'\n')
                    self.qtp_tx = True
                    self.clock.tick()
                    self.test_time = 0
                    self.qtp4_state = 3
            
            elif (self.qtp4_state == 3):
                if (self.qtp_tx == True):
                    qtp4_data = [163,self.speed,self.speed,0]
                    com_bot.send_ser_data(qtp4_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp4_data)+'\n')
                    self.qtp_tx = True
                    self.clock.tick()
                    self.test_time = 0
                    self.qtp4_state = 4
            
            elif (self.qtp4_state == 4):
                if (self.qtp_tx == True):
                    rho = abs(self.rho)
                    if self.rho != 0:
                        sign = int(self.rho/rho+1)
                    else:
                        sign = 2
                    qtp4_data = [177,rho,ord(self.rho_color),sign]
                    com_bot.send_ser_data(qtp4_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp4_data)+'\n')
                    self.qtp_tx = True
                    self.clock.tick()
                    self.test_time = 0
                    self.qtp4_state = 5
            
            elif (self.qtp4_state == 5):
                qtp4_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()                
                if qtp4_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp4_get)+'\n')
                    com_bot.send_ser_data(qtp4_get)
                    if (qtp4_get[0] == 145):
                        self.clock.tick()
                        self.test_time = 0
                        self.qtp4_state = 6
                        self.qtp_tx = True                        
                elif (self.test_time < 5000):
                    pass
                else:
                    self.clock.tick()
                    self.test_time = 0                    
                    self.qtp4_state = 6
                    self.qtp_tx = True
            
            elif (self.qtp4_state == 6):
                qtp4_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()                
                if qtp4_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp4_get)+'\n')
                    com_bot.send_ser_data(qtp4_get)
                    if (qtp4_get[0] == 146):
                        self.clock.tick()
                        self.test_time = 0
                        self.qtp4_state = 7
                        self.qtp_tx = True                        
                elif (self.test_time < 5000):
                    pass
                else:
                    self.clock.tick()
                    self.test_time = 0                    
                    self.qtp4_state = 7
                    self.qtp_tx = True
            
            elif (self.qtp4_state == 7):
                if (self.counter <= 10):
                    self.qtp4_state = 2
                    if (self.direction):                    
                        if (self.rho < 50):
                            self.rho += 20
                        else:
                            self.direction = not self.direction
                    else:                    
                        if (self.rho > -50):
                            self.rho -= 20
                        else:
                            self.direction = not self.direction
                    if (self.Bat >= 10):
                        self.Bat -= 10
                    else:
                        self.Bat = 0
                    if (self.speed >= self.V_op/10):
                        self.speed -= int(self.V_op/10)
                    else:
                        self.speed = 0
                    self.qtp4_state = 1
                    self.qtp_tx = True
                else:
                    self.clock.tick()
                    self.test_time = 0                    
                    self.qtp4_state = 8
                    self.qtp_tx = True
            
            else:
                qtp4_data = [1,0,0,0]
                com_bot.send_ser_data(qtp4_data)
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp4_data)+'\n')
                self.draw_status("Waiting for QTP selection. ",(176,230,134))
                boxes.default_color()
                lines.default_color()
                self.qtp4_state = 0
                buttons[6].clear_pushed()#
                self.qtp_tx = True
                self.qtp4_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP4: " + str(self.subsys)+'\n')
                
        elif self.subsys == 2:
            """QTP4 for MDPS subsystem.
            """
            if (self.qtp4_state == 0):
                self.draw_status("Running QTP 4. ",(176,230,134))
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Subsystem: " + str(self.subsys)+'\n')
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP4: " + str(self.subsys)+'\n')
                self.qtp_tx = True
                self.test_time = 0
                self.clock.tick()
                self.qtp4_state = 1
                com_bot.clear_ser_buffer()
                
            elif (self.qtp4_state == 1):
                if (self.qtp_tx == True):
                    qtp4_data = [112,0,0,0]
                    com_bot.send_ser_data(qtp4_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp4_data)+'\n')
                    self.qtp_tx = False
                    self.qtp4_state = 2
                    self.test_time = 0
                    self.clock.tick()
            
            elif (self.qtp4_state == 2):
                qtp4_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp4_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp4_get)+'\n')
                    com_bot.send_ser_data(qtp4_get)
                    if qtp4_get[0] == 96:
                        self.qtp_tx = True                    
                        self.V_op = qtp4_get[1]
                        print('Test. Set V_op as:', self.V_op)
                        self.speed = 2*self.V_op
                        self.qtp4_state = 3
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp4_state = 3
                    self.qtp_tx = True
            
            elif (self.qtp4_state == 3):
                qtp4_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp4_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp4_get)+'\n')
                    com_bot.send_ser_data(qtp4_get)
                    if qtp4_get[0] == 97:
                        self.qtp_tx = True
                        self.qtp4_state = 4
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp4_state = 4
                    self.qtp_tx = True
            
            elif (self.qtp4_state == 4):
                if (self.qtp_tx == True):
                    qtp4_data = [146,self.speed,self.speed,0]
                    com_bot.send_ser_data(qtp4_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp4_data)+'\n')
                    self.qtp_tx = False
                    self.qtp4_state = 5
                    self.test_time = 0
                    self.clock.tick()
            
            elif (self.qtp4_state == 5):
                qtp4_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp4_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp4_get)+'\n')
                    com_bot.send_ser_data(qtp4_get)
                    if qtp4_get[0] == 161:
                        self.qtp_tx = True
                        self.qtp4_state = 6
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp4_state = 6
                    self.qtp_tx = True
            
            elif (self.qtp4_state == 6):
                qtp4_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp4_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp4_get)+'\n')
                    com_bot.send_ser_data(qtp4_get)
                    if qtp4_get[0] == 162:
                        self.qtp_tx = True
                        self.qtp4_state = 7
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp4_state = 7
                    self.qtp_tx = True
            
            elif (self.qtp4_state == 7):
                qtp4_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()
                if qtp4_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp4_get)+'\n')
                    com_bot.send_ser_data(qtp4_get)
                    if qtp4_get[0] == 163:
                        self.qtp_tx = True
                        self.qtp4_state = 8
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp4_state = 8
                    self.qtp_tx = True
                    
            elif (self.qtp4_state == 8):    
                if self.speed > 2*self.V_op/10:
                    print('Test. Set speed = ', self.speed, 'V_op =', self.V_op)
                    self.speed -= int(abs(2*self.V_op/10))
                    self.qtp4_state = 4
                else:
                    self.qtp4_state = 9
                    
            else:
                qtp4_data = [1,0,0,0]
                com_bot.send_ser_data(qtp4_data)
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp4_data)+'\n')
                self.draw_status("Waiting for QTP selection. ",(176,230,134))
                boxes.default_color()
                lines.default_color()
                self.qtp4_state = 0
                buttons[6].clear_pushed()#
                self.qtp_tx = True
                self.qtp4_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP4: " + str(self.subsys)+'\n')
        else:
            self.draw_status("Waiting for QTP selection. ",(176,230,134))
            boxes.default_color()
            lines.default_color()
            self.qtp4_state = 0
            buttons[6].clear_pushed()#
            self.qtp_tx = True
            self.qtp4_pushed = False
    
    def qtp5(self,com_bot,boxes,lines,buttons):
        if self.subsys == 0:
            """ QTP5 for sensor subsystem.
            """
            if (self.qtp5_state == 0):
                self.draw_status("Running QTP 5. ",(176,230,134))
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Subsystem: " + str(self.subsys)+'\n')
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP5: " + str(self.subsys)+'\n')
                self.qtp_tx = True
                self.test_time = 0
                self.clock.tick()                       
                self.qtp5_state = 1
                boxes.change_color(WHITE)
                lines.change_color(self.race_color)
                self.counter = 0
                
            elif (self.qtp5_state == 1):
                if (self.qtp_tx == True):
                    qtp5_data = [145,1,0,0]
                    com_bot.send_ser_data(qtp5_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp5_data)+'\n')
                    self.qtp_tx = False
                    self.clock.tick()
                    self.test_time = 0
                    self.qtp5_state = 2
                    
            elif (self.qtp5_state == 2):
                qtp5_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()                
                if qtp5_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp5_get)+'\n')
                    com_bot.send_ser_data(qtp5_get)
                if (self.test_time < 5000):
                    pass
                else:                    
                    self.qtp5_state = 3
                    self.qtp_tx = True
                    
            elif (self.qtp5_state == 3):
                if (self.qtp_tx == True):
                    qtp5_data = [208,1,0,0]
                    com_bot.send_ser_data(qtp5_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp5_data)+'\n')
                    self.qtp_tx = False
                    self.clock.tick()
                    self.test_time = 0
                    self.qtp5_state = 4
                    self.qtp_tx = True
                    
            elif (self.qtp5_state == 4):
                if (self.qtp_tx == True):
                    qtp5_data = [163,0,0,0]
                    com_bot.send_ser_data(qtp5_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp5_data)+'\n')
                    self.qtp_tx = False
                    self.clock.tick()
                    self.test_time = 0
                    self.qtp5_state = 5
                    
            elif (self.qtp5_state == 5):
                qtp5_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()                
                if qtp5_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp5_get)+'\n')
                    com_bot.send_ser_data(qtp5_get)
                    if (qtp5_get[0] == 177):
                        self.qtp5_state = 6
                        self.qtp_tx = True                        
                elif (self.test_time < 5000):
                    pass
                else:                    
                    self.qtp5_state = 6
                    self.qtp_tx = True
                    
            else:
                self.draw_status("Waiting for QTP selection. ",(176,230,134))
                qtp5_data = [1,0,0,0]
                com_bot.send_ser_data(qtp5_data)
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp5_data)+'\n')
                boxes.default_color()
                lines.default_color()
                self.qtp5_state = 0
                buttons[7].clear_pushed()#
                self.qtp_tx = True
                self.qtp5_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP5: " + str(self.subsys)+'\n')
                
        elif self.subsys == 1:
            """ QTP5 for SC3 subsystem
            """
            if (self.qtp5_state == 0):
                self.draw_status("Running QTP 5. ",(176,230,134))
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Subsystem: " + str(self.subsys)+'\n')
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP5: " + str(self.subsys)+'\n')
                self.qtp_tx = True
                self.test_time = 0
                self.clock.tick()                       
                self.qtp5_state = 1
                boxes.change_color(WHITE)
                lines.change_color(self.race_color)
                self.counter = 0
                self.playing = False
                self.sound_time = 0
                
            elif (self.qtp5_state == 1):
                if (self.qtp_tx == True):
                    qtp5_data = [177,0,0,0]
                    com_bot.send_ser_data(qtp5_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp5_data)+'\n')
                    self.qtp_tx = False
                    self.clock.tick()
                    self.test_time = 0
                    self.qtp5_state = 2
                    self.qtp_tx = True
                    if self.sound_time > 1000:
                        self.counter += 1
                        if hasattr(self.sound, 'stop'):
                            self.stop_sound()
                            self.sound_time = 0
                        if self.counter >= 4:
                            self.qtp5_state = 8
                            self.qtp_tx = True
                    
            elif (self.qtp5_state == 2): # TODO              
                if self.counter == 1:
                    fs = 44100
                    self.f = 975 + 25*self.group_number - 50
                    t = np.linspace(0,5,5*fs)
                    y = 2048*np.sin(2*np.pi*self.f*t)
                    single = np.resize(y, (fs,)).astype(np.int16)
                    if not self.playing:
                        self.play_sound(single)
                        self.sound_time = 0
                    else:
                        self.sound_time += self.clock.tick()
                                        
                if self.counter == 2:                    
                    fs = 44100
                    self.f = 975 + 25*self.group_number + 50                    
                    t = np.linspace(0,5,5*fs)
                    y = 2048*np.sin(2*np.pi*self.f*t)
                    single = np.resize(y, (fs,)).astype(np.int16)
                    if not self.playing:
                        self.play_sound(single)
                        self.sound_time = 0
                    else:
                        self.sound_time += self.clock.tick()
                    
                elif self.counter == 3:
                    fs = 44100
                    self.f = 975 + 25*self.group_number                    
                    t = np.linspace(0,5,5*fs)
                    y = 2048*np.sin(2*np.pi*self.f*t)
                    single = np.resize(y, (fs,)).astype(np.int16)
                    if not self.playing:
                        self.play_sound(single)
                        self.sound_time = 0
                    else:
                        self.sound_time += self.clock.tick()
                self.qtp5_state = 3
                self.test_time = 0
                self.clock.tick()
                    
            
            elif (self.qtp5_state == 3):
                qtp5_get = com_bot.read_ser_data()
                tic = self.clock.tick()
                self.test_time += tic
                self.sound_time += tic
                if qtp5_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp5_get)+'\n')
                    com_bot.send_ser_data(qtp5_get)
                    if (qtp5_get[0] == 145):
                        if (qtp5_get[1] == 0):
                            self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " RefFreq: " + str(self.f)+'\n')
                            self.qtp5_state = 4
                            self.qtp_tx = True
                        else:
                            self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " RefFreq: " + str(self.f)+'\n')
                            self.qtp5_state = 5
                            self.qtp_tx = True
                            self.qtp_tx = True                            
                elif (self.test_time < 2500):
                    pass
                else:
                    if self.counter >= 3:
                        self.qtp5_state = 5
                    else:
                        self.qtp5_state = 4
                    self.qtp_tx = True
            
            elif (self.qtp5_state == 4):
                qtp5_get = com_bot.read_ser_data()
                tic = self.clock.tick()
                self.test_time += tic
                self.sound_time += tic
                if qtp5_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp5_get)+'\n')
                    com_bot.send_ser_data(qtp5_get)
                    if (qtp5_get[0] == 146):
                        self.qtp5_state = 1
                        self.qtp_tx = True 
                elif (self.test_time < 2500):
                    pass
                else:                    
                    self.qtp5_state = 1
                    self.qtp_tx = True
            
            elif (self.qtp5_state == 5):
                if (self.qtp_tx == True):
                    qtp5_data = [228,0,0,0]
                    com_bot.send_ser_data(qtp5_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp5_data)+'\n')
                    self.qtp_tx = False
                    self.clock.tick()
                    self.test_time = 0
                    self.qtp5_state = 6
                    self.qtp_tx = False
                    self.stop_sound()
            
            elif (self.qtp5_state == 6):
                qtp5_get = com_bot.read_ser_data()
                self.test_time += self.clock.tick()                
                if qtp5_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp5_get)+'\n')
                    com_bot.send_ser_data(qtp5_get)
                    if (qtp5_get[0] == 208):
                        if (qtp5_get[1] == 1):
                            self.qtp5_state = 7
                            self.qtp_tx = True
                        else:
                            self.qtp5_state = 6
                            self.qtp_tx = True
                elif (self.test_time < 10000):
                    pass
                else:                    
                    self.qtp5_state = 7
                    self.qtp_tx = True
                    
            elif (self.qtp5_state == 7):
                if self.counter >=3:
                    self.qtp5_state = 8
                    self.qtp_tx = True
                else:
                    self.qtp5_state = 1
                    self.qtp_tx = True
            
            else:
                qtp5_data = [1,0,0,0]
                com_bot.send_ser_data(qtp5_data)
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp5_data)+'\n')
                self.draw_status("Waiting for QTP selection. ",(176,230,134))
                self.stop_sound()
                boxes.default_color()
                lines.default_color()
                self.qtp5_state = 0
                buttons[7].clear_pushed()#
                self.qtp_tx = True
                self.qtp5_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP5: " + str(self.subsys)+'\n')
                
        elif self.subsys == 2:
            """QTP5 for MDPS subsystem
            """
            if (self.qtp5_state == 0):
                self.draw_status("Running QTP 5. ",(176,230,134))
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Subsystem: " + str(self.subsys)+'\n')
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Start QTP5: " + str(self.subsys)+'\n')
                self.qtp_tx = True
                self.test_time = 0
                self.clock.tick()
                self.qtp5_state = 1
                self.total_time = 0
                
            elif (self.qtp5_state == 1):
                if (self.qtp_tx == True):
                    qtp5_data = [112,0,0,0]
                    com_bot.send_ser_data(qtp5_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp5_data)+'\n')
                    self.qtp_tx = False
                    self.qtp5_state = 2
                    self.test_time = 0
                    tic = self.clock.tick()
                    self.total_time += tic
            
            elif (self.qtp5_state == 2):
                qtp5_get = com_bot.read_ser_data()
                tic = self.clock.tick()
                self.test_time += tic
                self.total_time += tic
                if qtp5_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp5_get)+'\n')
                    com_bot.send_ser_data(qtp5_get)
                    if qtp5_get[0] == 96:
                        self.qtp_tx = True                        
                        self.V_op = qtp5_get[1]
                        self.qtp5_state = 3
                        tic = self.clock.tick()
                        self.test_time = 0
                        self.total_time += tic
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp5_state = 3
                    self.qtp_tx = True
                    tic = self.clock.tick()
                    self.test_time = 0
                    self.total_time += tic
            
            elif (self.qtp5_state == 3):
                qtp5_get = com_bot.read_ser_data()
                tic = self.clock.tick()
                self.test_time += tic
                self.total_time += tic
                if qtp5_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp5_get)+'\n')
                    com_bot.send_ser_data(qtp5_get)
                    if qtp5_get[0] == 97:
                        self.qtp_tx = True
                        self.qtp5_state = 4
                        tic = self.clock.tick()
                        self.test_time = 0
                        self.total_time += tic
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp5_state = 4
                    self.qtp_tx = True
                    tic = self.clock.tick()
                    self.test_time = 0
                    self.total_time += tic
            
            elif (self.qtp5_state == 4):
                if (self.qtp_tx == True):
                    qtp5_data = [145,0,0,0]
                    com_bot.send_ser_data(qtp5_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp5_data)+'\n')
                    self.qtp_tx = True
                    self.qtp5_state = 5
                    self.test_time = 0
                    tic = self.clock.tick()
                    self.total_time += tic
                    
            elif (self.qtp5_state == 5):
                if (self.qtp_tx == True):
                    qtp5_data = [146,self.V_op,self.V_op,0]
                    com_bot.send_ser_data(qtp5_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp5_data)+'\n')
                    self.qtp_tx = False
                    self.qtp5_state = 6
                    self.test_time = 0
                    tic = self.clock.tick()
                    self.total_time += tic
            
            elif (self.qtp5_state == 6):
                qtp5_get = com_bot.read_ser_data()
                tic = self.clock.tick()
                self.test_time += tic
                self.total_time += tic
                if qtp5_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp5_get)+'\n')
                    com_bot.send_ser_data(qtp5_get)
                    if qtp5_get[0] == 161:
                        self.qtp_tx = True
                        self.qtp5_state = 7
                        tic = self.clock.tick()
                        self.test_time = 0
                        self.total_time += tic
                    else:
                        print('Error. State = ', self.qtp5_state, 'Data = ', qtp5_get)
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp5_state = 7
                    self.qtp_tx = True
                    tic = self.clock.tick()
                    self.test_time = 0
                    self.total_time += tic
            
            elif (self.qtp5_state == 7):
                qtp5_get = com_bot.read_ser_data()
                tic = self.clock.tick()
                self.test_time += tic
                self.total_time += tic
                if qtp5_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp5_get)+'\n')
                    com_bot.send_ser_data(qtp5_get)
                    if qtp5_get[0] == 162:
                        self.qtp_tx = True
                        self.qtp5_state = 8
                        tic = self.clock.tick()
                        self.test_time = 0
                        self.total_time += tic
                    else:
                        print('Error. State = ', self.qtp5_state, 'Data = ', qtp5_get)
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp5_state = 8
                    self.qtp_tx = True
                    tic = self.clock.tick()
                    self.test_time = 0
                    self.total_time += tic
            
            elif (self.qtp5_state == 8):
                qtp5_get = com_bot.read_ser_data()
                tic = self.clock.tick()
                self.test_time += tic
                self.total_time += tic
                if qtp5_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp5_get)+'\n')
                    com_bot.send_ser_data(qtp5_get)
                    if qtp5_get[0] == 163:
                        self.qtp_tx = True
                        self.qtp5_state = 9
                        tic = self.clock.tick()
                        self.test_time = 0
                        self.total_time += tic
                    else:
                        print('Error. State = ', self.qtp5_state, 'Data = ', qtp5_get)
                elif (self.test_time < 5000):
                    pass
                else:                            
                    self.qtp5_state = 9
                    self.qtp_tx = True
                    tic = self.clock.tick()
                    self.test_time = 0
                    self.total_time += tic
                    
            elif (self.qtp5_state == 9):
                print('Test. QTP5 Time check:',self.total_time,'ms')
                if (self.total_time <= 5000):
                    self.qtp5_state = 4
                    self.qtp_tx = True
                else:
                    self.qtp5_state = 10
                    self.qtp_tx = True
                    
            elif (self.qtp5_state == 10):
                if (self.qtp_tx == True):
                    qtp5_data = [145,1,0,0]
                    com_bot.send_ser_data(qtp5_data)
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp5_data)+'\n')
                    self.qtp_tx = False
                    self.qtp5_state = 11
                    self.test_time = 0
                    tic = self.clock.tick()
                    self.total_time += tic
                    
            elif (self.qtp5_state == 11):
                qtp5_get = com_bot.read_ser_data()
                tic = self.clock.tick()
                self.test_time += tic
                self.total_time += tic
                if qtp5_get != None:
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Read: " + str(qtp5_get)+'\n')
                    com_bot.send_ser_data(qtp5_get)
                    if qtp5_get[0] == 228:
                        self.qtp_tx = True
                        self.qtp5_state = 12
                        tic = self.clock.tick()
                        self.test_time = 0
                        self.total_time += tic
                elif (self.test_time < 10000):
                    pass
                else:                            
                    self.qtp5_state = 12
                    self.qtp_tx = True
                    tic = self.clock.tick()
                    self.test_time = 0
                    self.total_time += tic
            
            else:
                qtp5_data = [1,0,0,0]
                com_bot.send_ser_data(qtp5_data)
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Sent: " + str(qtp5_data)+'\n')
                self.draw_status("Waiting for QTP selection. ",(176,230,134))
                boxes.default_color()
                lines.default_color()
                self.qtp5_state = 0
                buttons[7].clear_pushed()#
                self.qtp_tx = True
                self.qtp5_pushed = False
                self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " End QTP5: " + str(self.subsys)+'\n')
        else:
            boxes.default_color()
            lines.default_color()
            self.qtp5_state = 0
            buttons[7].clear_pushed()
            self.qtp_tx = True
            self.qtp5_pushed = False
        
 
    def run(self, linegroup, buttongroup, boxgroup, iogroup, graphgroup, checkgroup, lines, boxes, buttons, ios, graphs, checkboxes):
        """The mainloop
        linegroup, buttongroup, boxgroup, iogroup, graphgroup, checkgroup, lines, boxes, buttons, ios, graphs, checkboxes
        """
        running = True
        self.draw_text("Resize line/box", boxes.rect.left, 0, (176,230,134))
        button0_pushed = False
        button1_pushed = False
        button2_pushed = False
        button3_pushed = False
        button4_pushed = False
        button5_pushed = False
        
        check1 = 0
        check2 = 0
        check3 = 0
        
        """Figure setup
        """
        x0 = np.linspace(0,2*math.pi,11)
        y0 = np.sin(x0)
        graphs[0].set_axis(min(x0), max(x0), min(y0), max(y0))
        graphs[0].clear()
        graphs[0].update(x0,y0,(0, 0, 255))
        
        x2 = self.marv.green_line[1,:]
        y2 = self.marv.green_line[0,:]
        graphs[1].set_axis(0, 5000, -200, 200)
        graphs[1].clear()
        graphs[1].update(x2,y2,(0, 255, 0))
        """Connection setup
        """
        connected = False
        reset = False
        lines.rect.centery = boxes.rect.centery #TODO
        lines.change_height(0)
        com_bot = com_client('localhost',65432)
        self.screen.blit(self.background, (0, 0))
        
        """QTP setup
        """
        self.line_y = lines.rect.centery
        
        """Run until end
        """
        while running:
            """Check for events. 
            """
            # milliseconds = self.clock.tick()
            # print(milliseconds,'milliseconds')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    buttongroup.update(pygame.mouse.get_pos(),1)
                    checkgroup.update(pygame.mouse.get_pos(),1)
                elif event.type == pygame.MOUSEBUTTONUP:
                    button0_pushed = buttons[0].get_pushed()
                    button1_pushed = buttons[1].get_pushed()
                    button2_pushed = buttons[2].get_pushed()
                    self.qtp1_pushed = buttons[3].get_pushed()
                    self.qtp2_pushed = buttons[4].get_pushed()
                    self.qtp3_pushed = buttons[5].get_pushed()
                    self.qtp4_pushed = buttons[6].get_pushed()
                    self.qtp5_pushed = buttons[7].get_pushed()
                    button3_pushed = buttons[8].get_pushed()
                    button4_pushed = buttons[9].get_pushed()
                    button5_pushed = buttons[10].get_pushed()
                    check1 = checkboxes[0].get_checked()
                    check2 = checkboxes[1].get_checked()
                    check3 = checkboxes[2].get_checked()
                    buttongroup.update(pygame.mouse.get_pos(),0)
                com_io = ios[0].handle_event(event)
                group_io = ios[1].handle_event(event)
                if (com_io != None):
                    com_bot.serial_port = com_io
                    com_io = None
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " COMport: " + str(com_bot.serial_port)+'\n')
                if (group_io != None):
                    self.group_number = int(group_io)
                    group_io = None
                    self.log_file.log_add(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " Group: " + str(self.group_number)+'\n')
                    
                   
                    
                    
            """ Determine selected subsystem from checkboxes.
            """
            if (check1):
                checkboxes[1].set_checked()
                checkboxes[2].set_checked()
                self.subsys = 0
            elif (check2):
                checkboxes[0].set_checked()
                checkboxes[2].set_checked()
                self.subsys = 1
            elif (check3):
                checkboxes[0].set_checked()
                checkboxes[1].set_checked()
                self.subsys = 2
            
            if (check1 + check2 + check3 > 1):
                check1 = 0
                check2 = 0
                check3 = 0
                checkboxes[0].set_checked()
                checkboxes[1].set_checked()
                checkboxes[2].set_checked()
                checkgroup.clear(self.act_surface, self.background)
                checkgroup.draw(self.act_surface)
                self.subsys = 3
            
            """Check if connect was pushed
            """
            if button0_pushed:                
                connected = not connected
                reset = not connected
                button0_pushed = not button0_pushed
                if connected:
                    self.draw_status("Connecting...",(176,230,134))
                    
                    com_bot.open_connections()
                    if (com_bot.ser_con_status):
                        self.draw_status("Connected. Waiting QTP selection.",(176,230,134))
                    else:
                        self.draw_status("Error connecting to serial.",(176,230,134))
                else:
                    pass
                
            """Change sensor box and line width
            """            
            if button1_pushed:
                button1_pushed = False
                buttons[1].get_pushed()
                if (boxes.rect.bottom < self.height - 190):
                    boxes.change_height(5)
                    lines.rect.centery = boxes.rect.centery
                
            if button2_pushed:
                button2_pushed = False
                buttons[2].get_pushed()
                if (boxes.rect.bottom > self.height/2 + 25):
                    boxes.change_height(-5)
                    lines.rect.centery = boxes.rect.centery
                    
            if button3_pushed:
                button3_pushed = False
                buttons[3].get_pushed()
                if (lines.rect.height < 0.25*boxes.rect.h):
                    lines.change_height(5)
                    
            if button4_pushed:
                button4_pushed = False
                buttons[4].get_pushed()
                if (lines.rect.height > 25):
                    lines.change_height(-5)
                    
            if button5_pushed:
                button5_pushed = False
                buttons[5].get_pushed()
                if self.race_color == GREEN_up:
                    self.race_color = RED_up
                    lines.change_color(RED_up)
                    self.draw_status("Race Colour: RED",(176,230,134))
                elif self.race_color == RED_up:
                    self.race_color = BLUE_up
                    lines.change_color(BLUE_up)
                    self.draw_status("Race Colour: BLUE",(176,230,134))
                elif self.race_color == BLUE_up:
                    self.race_color = GREEN_up
                    lines.change_color(GREEN_up)
                    self.draw_status("Race Colour: GREEN",(176,230,134))
                else:
                    self.race_color = GREEN_up
                    lines.change_color(GREEN_up)
                    self.draw_status("Race Colour: GREEN",(176,230,134))
            
            #Todo
            """Add button to select user module (Sensor, Motor or Control)
            and transmit this to the HUB when connected such that the HUB
            can deselect the drop in module.
            """
            if self.qtp1_pushed:
                # TODO Implement QTPs
                """When QTPs are released this button must be 
                implemented with the relevant QTP function. This will 
                remove all drop in modules from the HUB and this interface
                will alter the flow of the state machine to enforce the QTP. 
                """
                self.qtp1(com_bot,boxes,lines,buttons)
                
            if self.qtp2_pushed:                
                # TODO Implement QTPs from HUB
                """When QTPs are released this button must be 
                implemented with the relevant QTP function. This will 
                remove all drop in modules from the HUB and this interface
                will alter the flow of the state machine to enforce the QTP. 
                """
                # self.qtp2_pushed = False
                self.qtp2(com_bot,boxes,lines,buttons)
                
            if self.qtp3_pushed:
                """When QTPs are released this button must be 
                implemented with the relevant QTP function. This will 
                remove all drop in modules from the HUB and this interface
                will alter the flow of the state machine to enforce the QTP. 
                """
                self.qtp3(com_bot,boxes,lines,buttons,graphs)
                if not self.qtp3_pushed and self.subsys == 1:
                    x2 = self.marv.green_line[1,:]
                    y2 = self.marv.green_line[0,:]
                    x3 = self.marv.y[0,:]
                    y3 = self.marv.y[1,:]
                    graphs[1].clear()
                    graphs[1].update(x2,y2,(0, 255, 0))
                    graphs[1].update(x3,y3,(120, 0, 0))
                
            if self.qtp4_pushed:
                # TODO Implement QTPs
                """When QTPs are released this button must be 
                implemented with the relevant QTP function. This will 
                remove all drop in modules from the HUB and this interface
                will alter the flow of the state machine to enforce the QTP. 
                """
                self.qtp4(com_bot,boxes,lines,buttons)                
                
            if self.qtp5_pushed:
                # TODO Implement QTPs
                """When QTPs are released this button must be 
                implemented with the relevant QTP function. This will 
                remove all drop in modules from the HUB and this interface
                will alter the flow of the state machine to enforce the QTP. 
                """
                self.qtp5(com_bot,boxes,lines,buttons)
                
            """ If connect button has been pressed and a valid connection 
            was formed, run echo and gui.
            """
            if connected:
                """Graphs plotting and update
                """
                com_bot.process_serial()
                
            else:
                """Reset figures, disconnect coms
                """
                if reset:             
                    reset = False
                    lines.rect.center = boxes.rect.center
                    graphs[0].clear()
                    graphs[1].clear()
                    lines.default_color()
                    button0_pushed = False
                    button1_pushed = False
                    button2_pushed = False
                    button3_pushed = False
                    button4_pushed = False
                    
                    check1 = 0
                    check2 = 0
                    check3 = 0
                    checkboxes[0].set_checked()
                    checkboxes[1].set_checked()
                    checkboxes[2].set_checked()
                    checkgroup.clear(self.act_surface, self.background)
                    checkgroup.draw(self.act_surface)
                    self.subsys = 3
                    
                    self.qtp1_pushed
                    self.qtp2_pushed
                    self.qtp3_pushed
                    self.qtp4_pushed
                    self.qtp5_pushed
                    
                    buttons[0].get_pushed()
                    buttons[1].get_pushed()
                    buttons[2].get_pushed()
                    buttons[3].get_pushed()
                    buttons[4].get_pushed()
                    buttons[5].get_pushed()
                    buttons[6].get_pushed()
                    buttons[7].get_pushed()
                    buttons[8].get_pushed()
                    buttons[9].get_pushed()
                    buttons[10].get_pushed()
                    
                    self.qtp1_state = 0
                    self.qtp2_state = 0
                    self.qtp3_state = 0
                    self.qtp4_state = 0
                    self.qtp5_state = 0
                    self.qtp_tx = False
                    self.counter = 0
                    self.test_time = 0
                    self.ls = [0,1,2,3,4]
                    self.direction = True
                    
                    self.qtp1_pushed = False
                    self.qtp2_pushed = False
                    self.qtp3_pushed = False
                    self.qtp4_pushed = False
                    self.qtp5_pushed = False
                    self.qtp_color = WHITE
                    self.race_color = GREEN_up
                    self.line_y = 0
                    self.V_op = 50
                    self.Bat = 100
                    self.rho = 0
                    self.rho_color = 'G'
                    self.speed = 0
                    self.f = 0
                    
                    self.draw_status("Waiting for QTP selection.",(176,230,134))
                    # reset button
            
            """Update interface
            """
            buttongroup.clear(self.act_surface, self.background)            
            buttongroup.draw(self.act_surface)
            
            boxgroup.clear(self.act_surface, self.background)
            boxgroup.update()
            boxgroup.draw(self.act_surface)
            
            iogroup.clear(self.act_surface, self.background)
            iogroup.update()
            iogroup.draw(self.act_surface)
            
            top = boxes.rect.top
            bot = boxes.rect.bottom
            linegroup.clear(self.act_surface, self.background)          
            linegroup.update(top,bot)
            linegroup.draw(self.act_surface)
            
            graphgroup.clear(self.act_surface, self.background)
            graphgroup.draw(self.act_surface)
            
            checkgroup.clear(self.act_surface, self.background)
            checkgroup.draw(self.act_surface)
            
            pygame.display.flip()
            # self.screen.blit(self.background, (0, 0))       
            
        """ On exit, close connections
        """
        com_bot.close_connections()
        pygame.quit()
 
####
         
class InputBox(pygame.sprite.Sprite):
    """Inputbox sprite, Used for serial com selection
    """ 
    def __init__(self, x, y, w, h, text=''):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.COLOR_INACTIVE = (255,0,0)
        self.COLOR_ACTIVE = (0,255,0)        
        self.color = self.COLOR_INACTIVE
        self.text = text
        self.font = pygame.font.SysFont('mono', 18, bold=False)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False
        self.w = w
        self.h = h
        self.image = pygame.Surface((w, h))
        self.image.set_colorkey((0,0,0))
        self.image.fill((34,43,53))
        # self.rect = pygame.Rect(0, 0, w, h)
        self.font = pygame.font.SysFont('mono', 18, bold=False)
        
        text_surf = self.font.render(text, True, (255, 255, 255))        
        self.image.blit(text_surf, (5, 5))
        
        pygame.draw.rect(self.image, self.color, (0,0,w,h), 2)        
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        
        self.ret = None
        

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
            pygame.draw.rect(self.image, self.color, (0,0,self.w,self.h), 2)
            self.ret = None
        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.ret = self.text
                    self.text = 'Set: ' + self.text
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.ret = None
                    self.text = self.text[:-1]
                else:
                    self.ret = None
                    self.text += event.unicode
                # Re-render the text.
                self.image.fill((34,43,53))
                text_surf = self.font.render(self.text, True, self.color)
                self.image.blit(text_surf, (5, 5))
                pygame.draw.rect(self.image, self.color, (0,0,self.w,self.h), 2)
            else:
                 self.ret = None
        else:
             self.ret = None
        return self.ret

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width
        
class line(pygame.sprite.Sprite):
    """Green line in sensor box sprite
    """
    def __init__(self, x, y, length, width, speed_y=1, color=(0,0,255), border_width=0):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = x
        self.y = y
        self.length = length
        self.act_length = length
        self.speed_y = speed_y
        self.def_color = color
        self.color = color
        self.width = width
        self.border_width = border_width
        self.right_moving = True   
        
        self.image = pygame.Surface((length, width))
        self.image.set_colorkey((0,0,0))
        pygame.draw.rect(self.image, self.color, (0,0,length,width),border_width)
        
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        
    def update(self, top, bottom):
        if self.right_moving:
            if self.rect.bottom < bottom:
                self.rect.centerx += 0
                self.rect.centery += self.speed_y
            else:
                self.right_moving = False
        else:
            if self.rect.top > top:
                self.rect.centerx -= 0
                self.rect.centery -= self.speed_y
            else:
                self.right_moving = True
                
    def set_speed(self,speed):
        self.speed_y = speed
        
    def change_height(self,dy):
        self.x = self.rect.centerx
        self.y = self.rect.centery
        self.image = pygame.Surface((self.rect.width, self.rect.height+dy))
        self.image.set_colorkey((0,0,0))
        pygame.draw.rect(self.image, self.color, (0,0,self.rect.width,self.rect.height+dy),self.border_width)
        
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (self.x,self.y)
        
    def change_pos(self,dy):
        self.x = self.rect.centerx
        self.y = self.rect.centery + dy
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.set_colorkey((0,0,0))
        pygame.draw.rect(self.image, self.color, (0,0,self.rect.width,self.rect.height),self.border_width)
        
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (self.x,self.y)
        
    def change_color(self,color):
        self.x = self.rect.centerx
        self.y = self.rect.centery
        self.color = color
        self.image.fill(color)
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.set_colorkey((0,0,0))
        pygame.draw.rect(self.image, color, (0,0,self.rect.width,self.rect.height))
        
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (self.x,self.y)
        
    def default_color(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.set_colorkey((0,0,0))
        pygame.draw.rect(self.image, self.def_color, (0,0,self.rect.width,self.rect.height),self.border_width)
        
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (self.x,self.y)
                
class button(pygame.sprite.Sprite):
    """ UI buttons sprites. Can make better by passing functions to the update
    instead.
    """
    def __init__(self, x, y, length, width, text, alt_text, color=(0,0,255), border_width=0):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = x
        self.y = y
        self.length = length
        self.act_length = length
        self.color = color
        self.alt_color = (255,0,0)
        self.width = width
        self.border_width = border_width
        self.state = 0
        self.pushed = False
        self.text0 = text
        self.text1 = alt_text
        
        self.image = pygame.Surface((length, width))
        self.image.set_colorkey((0,0,0))
        self.image.fill((34,43,53))
        pygame.draw.rect(self.image, self.color, (0,0,length,width),border_width)
        
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.font = pygame.font.SysFont('mono', 18, bold=False)
        
        self.draw_text(self.text0)
        
    def update(self, mousepos, mouseclick):
        if (mouseclick == 1):            
            x_y = self.rect.topleft + self.rect.bottomright
            if x_y[0] < mousepos[0] < x_y[2] and x_y[1] < mousepos[1] < x_y[3]:
                self.pushed = True
                if (self.state == 0):
                    self.image.fill((34,43,53))
                    pygame.draw.rect(self.image, self.alt_color, (0,0,self.length,self.width),self.border_width)
                    self.draw_text(self.text1)
                    self.state = 1
                else:
                    self.image.fill((34,43,53))
                    pygame.draw.rect(self.image, self.color, (0,0,self.length,self.width),self.border_width)
                    self.draw_text(self.text0)
                    self.state = 0
            else:
                pass
        else:
            pass
        
    def draw_text(self,text):
        text_surf = self.font.render(text, True, (255, 255, 255))        
        text_rect = text_surf.get_rect()
        self.image.blit(text_surf, (self.rect.w/2-text_rect.w/2,self.rect.h/2-text_rect.h/2))
        
    def get_pushed(self):
        pushed = self.pushed
        if self.pushed:
            self.pushed = False
        return pushed
    
    def clear_pushed(self):
        self.image.fill((34,43,53))
        pygame.draw.rect(self.image, self.color, (0,0,self.length,self.width),self.border_width)
        self.draw_text(self.text0)
        self.state = 0
    
class check_box(pygame.sprite.Sprite):
    """ UI buttons sprites. Can make better by passing functions to the update
    instead.
    """
    def __init__(self, x, y, length, width, text, color=(0,0,255), border_width=0):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = x
        self.y = y
        self.length = length
        self.act_length = length
        self.color = color
        self.width = width
        self.border_width = border_width
        self.state = 0
        self.text = text
        
        self.image = pygame.Surface((length, width))
        self.image.set_colorkey((0,0,0))
        self.image.fill((34,43,53))
        pygame.draw.rect(self.image, self.color, (0,0,length,width),border_width)
        
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.font = pygame.font.SysFont('mono', 18, bold=False)
        
        self.draw_text(self.text)
        
    def update(self, mousepos, mouseclick):
        if (mouseclick == 1):            
            x_y = self.rect.topleft + self.rect.bottomright
            if x_y[0] < mousepos[0] < x_y[2] and x_y[1] < mousepos[1] < x_y[3]:
                if (self.state == 0):
                    self.image.fill((34,43,53))
                    pygame.draw.rect(self.image, (0,255,0), (0,0,self.length,self.width),self.border_width)
                    self.state = 1
                else:
                    self.image.fill((34,43,53))
                    pygame.draw.rect(self.image, self.color, (0,0,self.length,self.width),self.border_width)                    
                    self.state = 0
                self.draw_text(self.text)
            else:
                pass
        else:
            pass
        
    def draw_text(self,text):
        text_surf = self.font.render(text, True, (255, 255, 255))        
        text_rect = text_surf.get_rect()
        self.image.blit(text_surf, (self.rect.w/2-text_rect.w/2,self.rect.h/2-text_rect.h/2))
        
    def get_checked(self):
        return self.state
    
    def set_checked(self):
        self.state = 0
        self.image.fill((34,43,53))
        pygame.draw.rect(self.image, self.color, (0,0,self.length,self.width),self.border_width)
        self.draw_text(self.text)
        
class box(pygame.sprite.Sprite):
    """ Adjustable hight sensor box sprite.
    """
    def __init__(self, x, y, length, width, color=(0,0,255), border_width=0):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = x
        self.y = y
        self.length = length
        self.act_length = length
        self.color = color
        self.width = width
        self.border_width = border_width
        
        self.image = pygame.Surface((length, width))
        self.image.set_colorkey((0,0,0))
        pygame.draw.rect(self.image, self.color, (0,0,length,width),border_width)
        
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        
    def update(self):
        pass
    
    def change_height(self,dy):
        self.image = pygame.Surface((self.rect.width, self.rect.height+dy))
        self.image.set_colorkey((0,0,0))
        pygame.draw.rect(self.image, self.color, (0,0,self.rect.width,self.rect.height+dy),self.border_width)
        
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x,self.y)
    
    def change_color(self,color):
        self.image.fill(color)
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.set_colorkey((0,0,0))
        pygame.draw.rect(self.image, color, (0,0,self.rect.width,self.rect.height))
        
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x,self.y)
        
    def default_color(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.set_colorkey((0,0,0))
        pygame.draw.rect(self.image, self.color, (0,0,self.rect.width,self.rect.height),self.border_width)
        
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x,self.y)
        
class graph(pygame.sprite.Sprite):
    """Graph sprite. Faster plotting.
    """
    def __init__(self, x, y, length, width, color=(0,0,255), border_width=0):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = x
        self.y = y
        self.length = length
        self.act_length = length
        self.color = color
        self.width = width
        self.border_width = border_width
        
        self.image = pygame.Surface((length, width))
        self.image.set_colorkey((0,0,0))
        pygame.draw.rect(self.image, self.color, (0,0,length,width),border_width)
        
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.axis = (0,2*math.pi,-1,1)
        
    def update(self,x,y,color):
        
        line = []
        y_fac = (-y - self.axis[2])*(self.width)/(self.axis[3]-self.axis[2])
        x_fac = (x - self.axis[0])*(self.length)/(self.axis[1]-self.axis[0])
        # x_fac = np.linspace(0,self.length,len(y))
        
        y_p = np.floor(y_fac)
        x_p = np.floor(x_fac)
        for i,j in enumerate(zip(x_p,y_p),start = 0):
            line.append(j)
        
        pygame.draw.lines(self.image,color,False,line,self.border_width)
        # pass
    
    def set_axis(self,x0,x1,y0,y1):
        self.axis = (x0,x1,y0,y1)
        
    def clear(self):
        self.image.fill((34,43,53))
        
class com_client(object):
    """ TCP and serial coms object.
    """
    def __init__(self, ip, tcp_port):
        self.ser_tx_packet = [None,None,None,None]
        self.ser_rx_packet = [None,None,None,None]
        self.serial_port = 'COM1'
        self.BAUDRATE = 19200
        
        self.ser_buffer = ()   
        self.ser_tx_buffer = []
        self.tcp_con_status = False
        self.ser_con_status = False
        
        self.ser_con = serial.Serial()
    
    def open_connections(self):
        """Connect to the TCP/IP server
        """         
        # Create Serial connection
        try:
            self.ser_con = serial.Serial(
                port = self.serial_port,
                baudrate = self.BAUDRATE,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS,
                timeout=5
            )
            self.ser_con_status = True
        except:
            self.ser_con_status = False
        
        if not self.ser_con.isOpen():
            print('Connecting to:', self.serial_port, self.BAUDRATE)
            self.ser_con.open()
            
        if self.ser_con.isOpen():
            self.ser_con_status = True
            print('Connected to:', self.serial_port, self.BAUDRATE)
        
    def process_serial(self):
        if self.ser_con_status:
            if self.ser_con.isOpen():
                if self.ser_con.out_waiting:
                    pass
                else:
                    self.ser_con.write(self.ser_tx_buffer[:4])
                    self.ser_tx_buffer = self.ser_tx_buffer[4:]
                if (self.ser_con.in_waiting):
                    byte = self.ser_con.read_all()
                    if (byte != None):
                        self.ser_buffer += tuple(byte)
                        
    def send_ser_data(self,data):
        """Send data via serial
        """
        self.ser_tx_buffer += data
            
    def read_ser_data(self):
        """Get data from serial
        """        
        if len(self.ser_buffer) >= 4:
            self.ser_rx_packet = list(self.ser_buffer[0:4])
            self.ser_buffer = self.ser_buffer[4:]
            return self.ser_rx_packet
        else:
            return None
            
    def clear_ser_buffer(self):
        self.ser_buffer = ()

    def close_connections(self):
        """Close serial and TCP/IP connections
        """        
        if self.ser_con.isOpen():
            self.ser_con.close()
   
#### 

class MARV:
    def __init__(self,group_number,marv_wheel_radius,marv_axis_length,marv_max_rpm,marv_sensor_distance,marv_sensor_array_length,DropIns):
        self.group_number = group_number
        self.wheel_radius = marv_wheel_radius
        self.axis_length = marv_axis_length
        self.max_rpm = marv_max_rpm
        self.sensor_distance = marv_sensor_distance
        self.sensor_array_length = marv_sensor_array_length
        self.DropIns = DropIns
        self.x = np.array([0.0, 0.0, 0.0])
        self.u = np.array([0,0])
        self.dt = 0.01
        self.EOL = 0        
        self.state = 0
        self.run_sim = 1
        self.PID_constants = [5.0,2.0,0.1]
        self.new_packet = False
        
        self.mdps_ist = 0
        self.mdps_transmit = 0
        self.mdps_data_flag = 0
        self.mdps_data_flag_next = 0
        self.battery_level = 100
        self.mdps_pwm = np.array([0,0])
        self.mdps_battery_level = 100
        
        self.sc3_ist = 0
        self.sc3_transmit = 0
        self.sc3_set_point = np.array([0,0])
        self.sc3_data_flag = 0
        self.sc3_data_flag_next = 0
        self.sc3_control_update = 0
        self.sc3_display_update = 0
        self.sc3_cap_touch = 0
        self.sc3_obstacle = 0
        self.sc3_error_Array = np.zeros(50)
        self.sc3_race_colour = 'G'
        
        self.sens_ist = 0
        self.sens_transmit = 0
        self.sens_data_flag = 0
        self.sens_data_flag_next = 0
        self.sens_rho = 0
        
        self.green_line = self.generate_line()
        self.y = self.x.reshape(3,1)
        self.tol = 10
        
    def generate_line(self):
        index = 0
        x_end = 5000
        tol = 10
        length = int(x_end/tol + 1);
        green_line = np.zeros((2,length))
        green_line[0,0] = 0
        green_line[1,0] = 0
        random.seed()
        
        for i in range(tol, x_end + tol, tol):
            index += 1
            if (i > x_end/50):
                if (index%5 == 0):
                    green_line[0,index] = green_line[0,index-1] + 5*tol*(random.random() -0.5)
                    
                    if (green_line[0,index] < -150):
                        green_line[0,index] = -150
                    elif (green_line[0,index] > 150):
                        green_line[0,index] = 150
                    else:
                        green_line[0,index] = green_line[0,index]
                else:
                    green_line[0,index] = green_line[0,index-1]
                    
            green_line[1,index] = i
    
        green_line[0,:] = signal.savgol_filter(green_line[0,:], 53, 3)
        return green_line
        
    def Sens_Calc(self,green_line,tol):
        x = self.x[0]
        y = self.x[1]
        theta = self.x[2]
        gam = self.sensor_distance
        alpha = self.sensor_array_length
        
        xc = gam*math.cos(theta) + x
        yc = gam*math.sin(theta) + y   
        
        if (theta < -0.085) or (theta > 0.085):
            
           
            if (theta > 0):
                x1 = xc - alpha*math.cos(math.pi/2-theta)
                x2 = xc + alpha*math.cos(math.pi/2-theta)
                y1 = yc + alpha*math.sin(math.pi/2-theta)
                y2 = yc - alpha*math.sin(math.pi/2-theta)
            else:
                x1 = xc - alpha*math.sin(theta)
                x2 = xc + alpha*math.sin(theta)
                y1 = yc + alpha*math.cos(theta)
                y2 = yc - alpha*math.cos(theta)
            
            if (x2 > x1):
                x_s_start = round(x1,3)
                x_s_end = round(x2,3)
            else:
                x_s_start = round(x2,3)
                x_s_end = round(x1,3)
    
            m_s = (y1-y2)/(x1-x2)
            c_s = yc - m_s*xc        
    
            x1 = np.array(self.find(abs(green_line[1,:] - x_s_start), lambda x: x < tol))
            x2 = np.array(self.find(abs(green_line[1,:] - x_s_end), lambda x: x < tol))
            x_search_array = np.concatenate((x1, x2), axis = 0)
            
                        
            gl_x_i_start = int(min(x_search_array))
            gl_x_i_end = int(max(x_search_array))
            
            gl_x_s_start = green_line[1,gl_x_i_start]
            gl_x_s_end = green_line[1,gl_x_i_end]
            gl_y_s_start = green_line[0,gl_x_i_start]
            gl_y_s_end = green_line[0,gl_x_i_end]
            
            m_g = (gl_y_s_start-gl_y_s_end) / (gl_x_s_start-gl_x_s_end)
            c_g = gl_y_s_start - m_g * gl_x_s_start
            
            #solve g_line == sens_line
            x_solve = (c_s-c_g)/(m_g-m_s)
            y_solve = self.sens_line(x_solve,m_s,c_s)
    
            X = np.array([[x_solve,y_solve],[xc,yc]])
            rho = self.pdist(X)
#            #1print('DEBUG: rho_pdist: ',rho)
        else:
            x_s_start = round(xc,2)
            gl_x_s_start = min(self.find(abs(green_line[1,:]-x_s_start), lambda x: x < tol))
            
            rho = green_line[0,gl_x_s_start] - yc
#            #1print('DEBUG: rho_flat: ',rho)
        
        self.sens_rho = rho
        return round(rho,1)
    
    def MDPS_Calc(self):
        self.u = self.sc3_set_point
        return self.u
    
    def SC3_Calc(self):
        #Control Hidden Haha
        
        # Return
        out = [0.5*self.max_rpm, 0.5*self.max_rpm] 
        self.sc3_set_point = out
        return out
        
    
    def Model_Sim(self,dt):
        p = self.x
        u = self.u
        r = self.wheel_radius
        L = self.axis_length
        
        u_r = u[0]*2*math.pi/60
        u_l = u[1]*2*math.pi/60    
    
        dx =    np.array([(r/2) * (u_l + u_r) * math.cos(p[2]), (r/2) * (u_l + u_r) * math.sin(p[2]), (r/L) * (u_r - u_l)])
          
        self.x = p + dt * dx
        
        return self.x
    
    def Z1_MDPS_DropIn(self):
    #MDPS Drop in module. State transition, simulation and communication.
        # Run Motor Model Simulation
        #switch self.state
        
        self.mdps_battery_level = (self.mdps_battery_level - (0.05*sum(self.mdps_pwm)/200.0 + 0.001))
        self.MDPS_Calc()
        
    
    def Z2_SC3_DropIn(self):
    #SC3 Drop in module. State transition, simulation and communication.
        # Run SC3 Model Simulation
        #switch self.state
        
        self.SC3_Calc()
                
        
    
    def Z3_Sens_DropIn(self):
    #SC3 Drop in module. State transition, simulation and communication.
        # Run SC3 Model Simulation
        #switch self.state
        
        self.Sens_Calc(self.green_line,self.tol)  
        
    def Zz_MARV_HUB(self):
         
        
        """Race mode.
        """            
        ## Nonlinear MARV model simulation            
        x = self.Model_Sim(self.dt)
        
        self.y = np.concatenate((self.y, x.reshape(3,1)), axis=1) # Data logging
                
        
        ## MARV sensor simulation (Sensor drop-in)
        if (self.DropIns[0] == 1):
            self.Z3_Sens_DropIn()                
        ## MARV Motor Simulation (drop-in)
        if (self.DropIns[1] == 1):
            self.Z1_MDPS_DropIn()
        ## MARV HMI/control simulation (drop-in)
        if (self.DropIns[2] == 1):      
            pass #self.Z2_SC3_DropIn()
            
        ## Determine max offset
        
    
    def find_error(self):
        length = len(self.y[0,:])
        err = np.zeros((length,1))
        tol = self.green_line[1,1]-self.green_line[1,0]
        for i in range(length):
            y_x = self.y[0,i]
            y_y = self.y[1,i]
            
            x1 = np.array(self.find(abs(self.green_line[1,:] - y_x), lambda x: x < tol))
            
            x_i_start = min(x1)
            x_i_end = max(x1)
            y_s_start = self.green_line[0,x_i_start]
            y_s_end = self.green_line[0,x_i_end]
            
            err[i] = min([abs(y_y - y_s_start), (y_y - y_s_end)])
        return max(err)
            
    def control_validity(self,control_byte):
        library = [0,1,16,80,96,97,112,113,145,146,161,162,163,177,178,208,228]
        if control_byte in library: 
            return True 
        else: 
            return False
        
    def sens_line(self,x,m,c):
        return m*x+c
        
    def find(self,a, func):
        return [i for (i, val) in enumerate(a) if func(val)]
    
    def pdist(self,x):
        z = abs(x[0,1] - x[1,1])
        if (z != 0):
            sign = (x[0,1] - x[1,1])/z
            return math.sqrt((x[0,0] - x[1,0])**2 + (x[0,1] - x[1,1])**2)*sign
        else:
            return math.sqrt((x[0,0] - x[1,0])**2 + (x[0,1] - x[1,1])**2)   
   
class log(object):
    def __init__(self,name):
        self.f = open(name, "a")
    
    def log_add(self,text):
        self.f.write(text)
    
    def close_file(self):
        self.f.close()
        
####
 
def main(width,height):
    """HUB Client Interface
    """   
    sensor_width = 200
    margin = 25
    line_height = 25
    
    view = pygameView(width,height)
     
    view.draw_static()    
    view.draw_text("HUB Client. Click connect.",0,0,(176,230,134))
    
    view.set_draw_dynamic()    
           
    # Create graphs
    graphgroup = pygame.sprite.Group()
    graph.groups = graphgroup
    graph01 = graph(margin, margin, 640, 240, (255, 0, 0),2)
    graph02 = graph(margin, 2*margin + 240, 640, 240, (255, 0, 0),2)

    # Create adjustable sensor box
    boxgroup = pygame.sprite.Group()
    box.groups = boxgroup
    box01 = box(graph01.rect.right+margin, 3*margin, sensor_width, graph02.rect.bottom- 3*margin, (255, 0, 0),2)

    # Create moving track line
    linegroup = pygame.sprite.Group()
    line.groups = linegroup
    line01 = line(box01.rect.left, margin, sensor_width, line_height, 0, (0, 255, 0))

    # Create buttons for connecting and ui control
    buttongroup = pygame.sprite.Group()
    button.groups = buttongroup
    button01 = button(margin, graph02.rect.bottom+margin, 100, 50, "Connect", "Reset", (20,100,160),2)
    button02 = button(box01.rect.left, box01.rect.top-margin-10, 50, 25, "+", "+", (20,100,160),2)
    button03 = button(box01.rect.right-50, box01.rect.top-margin-10, 50, 25, "-", "-", (20,100,160),2)
    
    # Create input box
    iogroup = pygame.sprite.Group()
    InputBox.groups = iogroup
    io01 = InputBox(button01.rect.right+50,button01.rect.top,140,32,'COM1')
    io02 = InputBox(button01.rect.right+50,io01.rect.bottom +50,140,32,'#')

    # Create QTP buttons
    placeholder05 = button(width-3*margin, button01.rect.top, 50, 50, "QTP5", "QTP5", (198,112,224),2)
    placeholder04 = button(placeholder05.rect.left-3*margin, graph02.rect.bottom+margin, 50, 50, "QTP4", "QTP4", (198,112,224),2)
    placeholder03 = button(placeholder04.rect.left-3*margin, graph02.rect.bottom+margin, 50, 50, "QTP3", "QTP3", (198,112,224),2)
    placeholder02 = button(placeholder03.rect.left-3*margin, graph02.rect.bottom+margin, 50, 50, "QTP2", "QTP2", (198,112,224),2)
    placeholder01 = button(placeholder02.rect.left-3*margin, graph02.rect.bottom+margin, 50, 50, "QTP1", "QTP1", (198,112,224),2)
    
    placeholder05.alt_color = (0,255,0)
    placeholder04.alt_color = (0,255,0)
    placeholder03.alt_color = (0,255,0)
    placeholder02.alt_color = (0,255,0)
    placeholder01.alt_color = (0,255,0)
    
    # More UI control buttons
    button04 = button(button02.rect.right+10, box01.rect.top-margin-10, 25, 25, "+", "+", (20,100,160),2)
    button05 = button(button03.rect.left-35, box01.rect.top-margin-10, 25, 25, "-", "-", (20,100,160),2)
    
    button06 = button(button04.rect.right+5, box01.rect.top-margin-10, 25, 25, "C", "C", (0,255,0),2)
    
    #UI Checkboxes
    checkgroup = pygame.sprite.Group()
    check_box.groups = checkgroup
    # x, y, length, width, text, color=(0,0,255), border_width=0
    check01 = check_box(placeholder01.rect.left, placeholder01.rect.bottom + margin, 50, 25, "Sens", (198,112,224),2)
    check02 = check_box(check01.rect.right + margin, placeholder01.rect.bottom + margin, 50, 25, "SC3", (198,112,224),2)
    check03 = check_box(check02.rect.right + margin, placeholder01.rect.bottom + margin, 50, 25, "MDPS", (198,112,224),2)
    
    boxes = (box01)
    lines = (line01)
    buttons = (button01,button02,button03,placeholder01,placeholder02,placeholder03,placeholder04,placeholder05,button04,button05, button06)
    ios = (io01,io02)
    graphs = (graph01, graph02)
    checkboxes = (check01, check02, check03)
    view.run(linegroup,buttongroup,boxgroup,iogroup,graphgroup,checkgroup,lines,boxes,buttons,ios,graphs,checkboxes)
 
####
     
if __name__ == '__main__':
 
    main(960,720)
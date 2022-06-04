from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import cv2

import socket

import ctypes
import _ctypes
import pygame
import sys
import numpy as np
import _thread as thread


class DepthRuntime(object):

    esp_ip_address = "192.168.0.18"  # Change to applicable
    esp_port       = 80            # Change to applicable
    zones_dict = {
            'slider_1':{
                'x': 251,
                'y': 210,
                'w': 4,
                'h': 50,
                'pos': (0,0),
                'sens': 100,
                'color': 'red',
                'cal': [],
                'inv': True,
                'offset': 60
            },
        }

    def __init__(self):
        pygame.init()

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Loop until the user clicks the close button.
        self._done = False

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Kinect runtime object, we want only color and body frames 
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Depth)

        # back buffer surface for getting Kinect depth frames, 8bit grey, width and height equal to the Kinect color frame size
        self._frame_surface = pygame.Surface((self._kinect.depth_frame_desc.Width, self._kinect.depth_frame_desc.Height), 0, 24)
        print(self._kinect.depth_frame_desc.Width, self._kinect.depth_frame_desc.Height)
        # here we will store skeleton data 
        self._bodies = None
        
        # Set the width and height of the screen [width, height]
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._kinect.depth_frame_desc.Width, self._kinect.depth_frame_desc.Height), 
                                                pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.esp_ip_address, self.esp_port))


        pygame.display.set_caption("Kinect for Windows v2 depth")



    def draw_depth_frame(self, frame, target_surface):
        if frame is None:  # some usb hub do not provide the infrared image. it works with Kinect studio though
            return
        target_surface.lock()
        f8=np.uint8(frame.clip(1,4000)/16.)
        frame8bit=np.dstack((f8,f8,f8))
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame8bit.ctypes.data, frame8bit.size)
        del address
        target_surface.unlock()
    
    
    def check_zones(self, arr):
        for key in self.zones_dict:
            v = self.zones_dict[key]
            if key[:6] == 'slider':
                v['color'] = 'red'
                slider_box = self.frame_to_box(arr, [[v['x'], v['y']],[v['x'] + v['w'], v['y'] + v['h']]])[0]
                count = 0
                slide_val = 0
                if len(slider_box) < len(slider_box[0]):
                    for i in range(len(slider_box[0])):
                        avg = (slider_box[0][i] + slider_box[1][i] + slider_box[2][i] + slider_box[3][i]) / 4
                        if avg < v['cal'][i] and avg > v['cal'][i] - v['sens']:
                            count += 1
                            slide_val += i
                    if count > 5:
                        #print(count)
                        #print(slide_val / count)
                        val = slide_val/count
                        if v['inv']:
                            val = v['w'] - val
                        try:
                            self.s.send(int(np.interp((slide_val / count), [0,v['w']], [0,100])).to_bytes(1, 'little'))
                        except:
                            print("Reconnecting")
                            try:
                                self.s.connect((self.esp_ip_address, self.esp_port))
                            except:
                                print("Failll")
                        v['pos'] = ((slide_val / count), 0)
                        v['color'] = 'green'
                else:
                    for i in range(len(slider_box)):
                        sum = 0
                        avg_den = 0
                        for j in range(len(slider_box[0])):
                            if slider_box[i][j] > (v['cal'][i] - (2 * v['sens'])):
                                avg_den += 1
                                sum += slider_box[i][j]
                        avg = sum/avg_den if avg_den != 0 else v['cal'][i] - v['sens']
                        if avg < v['cal'][i] and avg > v['cal'][i] - v['sens']:
                            print(slider_box[i][0], slider_box[i][1], slider_box[i][2], slider_box[i][3])
                            count += 1
                            slide_val += i
                    if count > 5:
                        print(count)
                        val = slide_val/count
                        if v['inv']:
                            val = v['h'] - val
                        try:
                            self.s.send(int(np.interp(val, [0,v['h']], [0,100])).to_bytes(1, 'little'))
                        except:
                            print("Reconnecting")
                            try:
                                self.s.connect((self.esp_ip_address, self.esp_port))
                            except:
                                print("Failll")
                        #print(int(np.interp((slide_val / count), [0,v['h']], [0,19])).to_bytes(1, 'little')[0])
                        v['pos'] = (0, (slide_val/count))
                        v['color'] = 'green'


    def calibrate_zones(self, arr, calibrate=10):
        for key in self.zones_dict:
            v = self.zones_dict[key]
            if key[:6] == 'slider':
                slider_box = self.frame_to_box(arr, [[v['x'], v['y']],[v['x'] + v['w'], v['y'] + v['h']]])[0]
                if len(slider_box) < len(slider_box[0]):
                    for i in range(len(slider_box[0])):
                        avg = (slider_box[0][i] + slider_box[1][i] + slider_box[2][i] + slider_box[3][i]) / 4
                        if calibrate == 0:
                            v['cal'] = [0] * v['w']
                        v['cal'][i] += avg
                        if calibrate == 9:
                            v['cal'][i] /= 10
                            v['cal'][i] -= v['offset']
                else:
                    for i in range(len(slider_box)):
                        sum = 0
                        for j in range(len(slider_box[0])):
                            sum += slider_box[i][j]
                        avg = sum/4
                        if calibrate == 0:
                            v['cal'] = [0] * v['h']
                        v['cal'][i] += avg
                        if calibrate == 9:
                            v['cal'][i] /= 9
                            v['cal'][i] -= v['offset']
                
    def check_slider(self, arr, pX, pY, zX, zY, back_limit):

        

        slider = [[pX,pY],[zX,zY]]
        slider_box = self.frame_to_box(arr, slider)[0]
        count = 0
        slide_val = 0
        if len(slider_box) < len(slider_box[0]):
            for i in range(len(slider_box[0])):
                avg = (slider_box[0][i] + slider_box[1][i] + slider_box[2][i] + slider_box[3][i]) / 4
                if avg < back_limit and avg > back_limit - 100:
                    count += 1
                    slide_val += i
            if count > 5:
                print(slide_val / count)
                return [True, pX + (slide_val / count), pY]
        else:
            for i in range(len(slider_box)):
                sum = 0
                for j in range(len(slider_box[0])):
                    sum += slider_box[i][j]
                avg = sum/4
                if avg < back_limit and avg > back_limit - 100:
                    count += 1
                    slide_val += i
            if count > 5:
                print(slide_val / count)
                return [True, pX, pY + (slide_val / count)]

        
        return [False, None, None]
        

    def check_box(self, arr, pX, pY, width, back_limit):
        box = [[pX,pY],[pX+width,pY+width]]
        box_frame, avg = self.frame_to_box(arr, box)
        #img = np.copy(np.array(box_frame, dtype=np.uint8))
        #edges = cv2.Canny(img,70,110,apertureSize = 3)

        if avg < back_limit and avg > back_limit - 100:
            return True
        return False

    def frame_to_box(self, frame, box):
        w = box[1][0] - box[0][0]
        h = box[1][1] - box[0][1]
        ox = box[0][0]
        oy = box[0][1]
        ret = [None]*h
        tot = 0
        skip = 0
        for y in range(h):
            row = [None] * w
            for x in range(w):
                row[x] = frame[oy+y][ox+x]
                tot += row[x]
                if row[x] == 0:
                    skip += 1
            ret[y] = row
        avg = tot / (w*h-skip)
        #print(avg)
        return (ret, avg)


    def run(self):
        # -------- Main Program Loop -----------
        box_color = pygame.color.THECOLORS["red"]
        slide_color = pygame.color.THECOLORS["red"]
        slideX = 256
        slideY = 180
        frame = None
        cal_itr = 0

        
        while not self._done:
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._done = True # Flag that we are done so we exit this loop

                elif event.type == pygame.VIDEORESIZE: # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'], 
                                                pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)
                    
            
            # --- Getting frames and drawing  
            if self._kinect.has_new_depth_frame():
                box_color = pygame.color.THECOLORS["red"]
                slide_color = pygame.color.THECOLORS["red"]
                frame = np.reshape(self._kinect.get_last_depth_frame(), (424, 512))
                self.draw_depth_frame(frame, self._frame_surface)
                if cal_itr <= 9:
                    self.calibrate_zones(frame, cal_itr)
                    cal_itr += 1
                self.check_zones(frame)


                #slHor = self.check_slider(frame, 256, 180, 316, 184, 3900)
                #if slHor[0]:
                #    slide_color = pygame.color.THECOLORS["green"]
                #    slideX = slHor[1]
                #    slideY = slHor[2]
                #if self.check_box(frame, 380,204,15, 1000):
                #    box_color = pygame.color.THECOLORS["green"]


                x, y = pygame.mouse.get_pos()
                #print(x, y, frame[y][x])
                frame = None

            self._screen.blit(self._frame_surface, (0,0))
            for key in self.zones_dict:
                el = self.zones_dict[key]
                pygame.draw.rect(self._screen, el['color'], pygame.Rect(el['x'],el['y'], el['w'], el['h']))
                pygame.draw.rect(self._screen, el['color'], pygame.Rect(el['x'] + el['pos'][0] - 2, el['y'] + el['pos'][1] - 2, 8, 8))


            pygame.display.update()

            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 60 frames per second
            self._clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()


__main__ = "Kinect v2 depth"
game =DepthRuntime();
game.run();

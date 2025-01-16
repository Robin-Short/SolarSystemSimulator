'''
buttons lybrary for Solar System Simulator
'''

import numpy as np
import pyglet
from pyglet.window import key
from pyglet.window import mouse

deltaX = 250
deltaY = 24
margin = 16


alphabet = {
        '97' : 'a',
        '98' : 'b',
        '99' : 'c',
        '100' : 'd',
        '101' : 'e',
        '102' : 'f',
        '103' : 'g',
        '104' : 'h',
        '105' : 'i',
        '106' : 'j',
        '107' : 'k',
        '108' : 'l',
        '109' : 'm',
        '110' : 'n',
        '111' : 'o',
        '112' : 'p',
        '113' : 'q',
        '114' : 'r',
        '115' : 's',
        '116' : 't',
        '117' : 'u',
        '118' : 'v',
        '119' : 'w',
        '120' : 'x',
        '121' : 'y',
        '122' : 'z'
        }
ALPHABET = {
        '1097' : 'A',
        '1098' : 'B',
        '1099' : 'C',
        '1100' : 'D',
        '1101' : 'E',
        '1102' : 'F',
        '1103' : 'G',
        '1104' : 'H',
        '1105' : 'I',
        '1106' : 'J',
        '1107' : 'K',
        '1108' : 'L',
        '1109' : 'M',
        '1110' : 'N',
        '1111' : 'O',
        '1112' : 'P',
        '1113' : 'Q',
        '1114' : 'R',
        '1115' : 'S',
        '1116' : 'T',
        '1117' : 'U',
        '1118' : 'V',
        '1119' : 'W',
        '1120' : 'X',
        '1121' : 'Y',
        '1122' : 'Z'
        }
numbers = {
        '48' : 0,
        '49' : 1,
        '50' : 2,
        '51' : 3,
        '52' : 4,
        '53' : 5,
        '54' : 6,
        '55' : 7,
        '56' : 8,
        '57' : 9
        }

class Button: 
    def __init__(self, text, save, update, info=[''], kind='none', value=0, x=0, y=0, binValues = [True, False]):
        '''
        kind can be 'click', 'insert', 'singolAction' or 'none'
                 are the two value who can are switched by 'click' action if kind == 'click'
        '''
        self.save = save
        self.updateFun = update
        self.text = text
        self.info = info
        self.xy = x, y
        self.value = value
        self.kind = kind
        self.binValues = binValues
        self.infoView = False
        self.writing = False
        self.selected = False
        
    def update(self):
        self.updateFun(self)
    def rightClick(self):
        self.infoView = False if self.infoView else True
    def click(self):
        if self.kind == 'none':
            pass
        elif self.kind == 'singleAction':
            self.save()
        elif self.kind == 'click':
            self.value = self.binValues[1] if self.value == self.binValues[0] else self.binValues[0]
            self.save(self.value)
        elif self.kind == 'insert':
            self.writing = not self.writing
        
            
    def isSelected(self, x, y):
        if self.xy[0] <= x <= self.xy[0] + deltaX and self.xy[1] <= y <= self.xy[1] + deltaY:
            return True
        else:
            return False

    def insert(self, ch):
        if self.kind == 'insert' and self.writing:
            if ch == key.RETURN:
                '''variable = self.value'''
                self.writing = False
                self.save(self.value)
            elif ch == key.BACKSPACE:
                if type(self.value) == str:
                    self.value = self.value[0:-1] if len(self.value) > 1 else ''
                else:
                    strNumb = str(self.value)
                    if len(strNumb) == 1 or (len(strNumb) == 3 and strNumb[0:2] == '0.'):
                        self.value = 0
                    else:
                        strNumb = strNumb[0:-2] if strNumb[-2] == '.' else strNumb[0:-1]
                        self.value = float(strNumb) if '.' in strNumb else int(strNumb)
                            
            elif str(ch) in alphabet.keys():
                self.value += str(alphabet[str(ch)])
            elif str(ch) in ALPHABET.keys():
                self.value += str(ALPHABET[str(ch)])
            elif str(ch) in numbers.keys():
                self.value *= 10
                self.value += numbers[str(ch)]
        
    def draw(self):
        if self.kind == 'singleAction':
            txt = str(self.text)
        else:
            txt = str(self.text) + ': ' + str(self.value)
        if self.kind == 'insert' and self.writing:
            txt += '_'
        dim = 24 if self.selected else 16
        text = pyglet.text.Label(txt,font_size=dim, x=self.xy[0], y=self.xy[1])
        text.draw()
        
show = False
def saveShow(x):
    global show; show = x
    
def upShow(b):
    b.value = show
    
infoShow = ['Click to view all buttons of MENU']
    
class Buttons:
    def __init__(self, listButtons, w, h):
        showB = Button('SHOW MENU', saveShow, upShow, infoShow, 'click', show, margin, h - margin - deltaY)
        self.buttons = [showB] + listButtons
        self.w = w
        self.h = h
        
    def add(self, b):
        self.buttons.append(b)
        
    def update(self):
        for b in self.buttons:
            if not b.writing:
                b.update()
        
    def draw(self):
        x = margin * 2
        y = self.h - 2 * margin - 2 * deltaY
        writingCounter = 0; infoCounter = 0
        self.buttons[0].draw()
        step = min(deltaY + margin, self.h // len(self.buttons))
        if show:
            for i in range(1,len(self.buttons)):
                b = self.buttons[i]
                if writingCounter > 0:
                    b.writing = False
                if b.writing:
                    writingCounter += 1
                if infoCounter > 0:
                    b.infoView = False
                if b.infoView:
                    infoCounter += 1
                    xx = self.w // 4 + margin
                    yy = margin
                    text = pyglet.text.Label('Right click on relative button to hide help.',font_size=16, x=xx - 4 * margin, y=yy)
                    text.draw()
                    for i in range(len(b.info)):
                        yy += (deltaY + margin)
                        text = pyglet.text.Label(b.info[-1 - i],font_size=20, x=xx, y=yy)
                        text.draw()
                    text = pyglet.text.Label(b.text + (' (HELP)'),font_size=24, x=xx - 4 * margin, y=yy + deltaY + margin)
                    text.draw()
                b.xy = x, y
                b.draw()
                y -= step
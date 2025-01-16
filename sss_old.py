
"""
Solar System Simulator

Created on Sat Oct 31 12:46:34 2020

Initial Condition at ?

@author: robins
"""

import numpy as np
import pyglet
from pyglet.gl import *
from pyglet.window import key
from pyglet.window import FPSDisplay

G = 6.67 * 10 ** -11
T = 0
dt_start = 10
dt = dt_start
SIZE = 256
CENTER = 'Sun'
Dx = 8
MEMORY_STEPS = 150

class Body:
    def __init__(self, m, r, p, pDot, name = False, color = (0,0,0,0)):
        self.name = name
        self.img = pyglet.resource.image(name + '.png')
        self.r = r
        self.m = m
        self.p = np.array(p)
        self.pDot = np.array(pDot)
        self.color = color
    
bodies = {
        'Sun' :     Body(332950,    0.3,    (0., 0.),       (0.0000, 0.00000),      'Sun',      (255, 200, 0, 0.8)),
        'Mercury' : Body(0.0553,    0.071,  (0., 0.33),     (0.0080, -0.00001),     'Mercury',  (223, 16, 28, 0.8)),
        'Venus' :   Body(0.815,     0.1,    (0., 0.66),     (0.0060, 0.00002),      'Venus',    (210, 141, 0, 0.8)),
        'Earth' :   Body(1,         0.09,   (0., 1.00),     (0.0050, 0.00000),      'Earth',    (0, 135, 255, 0.8)),
        'Mars' :    Body(0.1074,    0.083,  (0., 1.33),     (0.0040, -0.000012),    'Mars',     (169, 63, 28, 0.8)),
        'Jupiter' : Body(318,       0.25,   (0., 1.66),     (0.0040, -0.000010),    'Jupiter',  (156, 99, 0, 0.8)),
        'Saturn' :  Body(95.1608,   0.22,   (0., 2.00),     (0.0032, 0.000017),     'Saturn',   (239, 166, 0, 0.8)),
        'Uranus' :  Body(14.5357,   0.125,  (0., 2.33),     (0.0031, 0.000011),     'Uranus',   (0, 166, 163, 0.8)),
        'Neptune' : Body(17.148,    0.122,  (0., 2.66),     (0.0028, 0.000000),    'Neptune',   (0, 166, 220, 0.8))
        }

def versor(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm
def field(bodies, p, target = False):
    p = np.array(p)
    f = np.array((0.,0.))
    for name in bodies.keys():
        if not target or name != target.name:
            body = bodies[name]
            dist = np.linalg.norm(body.p - p)
            if dist > 0:
                factor = G * (body.m / (dist ** 3))
                f += factor * (body.p - p)
    return f

def F(q, bodies, target):
    return np.array(list(q[2:4]) + list(field(bodies, q[0:2], target)))

def update():
    global bodies, T
    T += dt
    for name in bodies.keys():
        body = bodies[name]
        q = np.array(list(body.p) + list(body.pDot))
        q1 = F(q, bodies, body) * dt
        q2 = F(q + 0.5 * q1, bodies, body) * dt
        q3 = F(q + 0.5 * q2, bodies, body) * dt
        q4 = F(q + q3, bodies, body) * dt
        q += (q1 + 2 * q2 + 2 * q3 + q4) / 6
        bodies[name].p, bodies[name].pDot = q[0:2], q[2:4]
        if orbits[name] == [] or np.linalg.norm(pixPos(bodies, bodies[name].p) - orbits[name][-1]) > Dx:
            orbits[name] +=[(pixPos(bodies, bodies[name].p))]
            if len(orbits[name]) > MEMORY_STEPS:
                orbits[name] = orbits[name][1:len(orbits[name]) + 1]
                


window = pyglet.window.Window(fullscreen = True)
fps_display = FPSDisplay(window)
WIDTH, HEIGHT = window.get_size()
MARGIN = 32
MID_POINT = np.array((WIDTH // 2, HEIGHT // 2))

def maxDistSun(bodies):
    d = 0.001
    for name in bodies.keys():
        d = max(d, np.linalg.norm(bodies[CENTER].p - bodies[name].p))
    return d

scaleFactor = (0.5 * HEIGHT - MARGIN) // maxDistSun(bodies)
#zero = np.array((0,0))

def pixPos(bodies, p):
    q = np.array(p) - bodies[CENTER].p
    return q * scaleFactor + MID_POINT

def realPos(bodies, p):
    q = np.array(p) - MID_POINT
    return q / scaleFactor

def angle(v):
    z = v[0] + v[1] * 1j
    return int(np.angle(z, deg = True))
fieldData = []
def drawField(bodies, nx, ny):
    global fieldData
    fieldData = []
    arrow = pyglet.resource.image('arrow.png')
    dx = WIDTH // nx
    dy = HEIGHT // ny
    for i in range(nx):
        raw = []
        for j in range(ny):
            x, y = realPos(bodies, (i * dx, j * dy))
            direction = field(bodies, np.array((x, y)))
            x, y = pixPos(bodies, (x, y))
            raw += [direction]
            alpha = angle(direction)
            module = np.linalg.norm(direction)
            #print(alpha)
            sprite = pyglet.sprite.Sprite(arrow, x - dx // (2 * SIZE), y - dy // (2 * SIZE))
            sprite.update(scale = 0.5 * min(1, 100000 * module), rotation = alpha)
            sprite.draw()
        fieldData += [raw]
        
orbits = {
        'Sun' :     [],
        'Mercury' : [],
        'Venus' :   [],
        'Earth' :   [],
        'Mars' :    [],
        'Jupiter' : [],
        'Saturn' :  [],
        'Uranus' :  [],
        'Neptune' : []
        }

frames = 0
keys = key.KeyStateHandler()
window.push_handlers(keys)
@window.event
def on_draw():
    global frames
    window.clear()
    fps_display.draw()
    timeText = pyglet.text.Label('Time: ' + str(T),font_name='Times New Roman',font_size=24,x = 16, y = bt.margin)
    timeText.draw()
    #drawField(bodies, 20, 10)
    for name in bodies.keys():
        if len(orbits[name]) > 1:
            glBegin(GL_LINES)
            r, g, b, a = np.array(bodies[name].color) / 255
            glColor4f(r, g, b, a)
            for i in range(0,len(orbits[name])-1):
                # create a line, x,y
                x1, y1 = orbits[name][i]
                x2, y2 = orbits[name][i+1]
                glVertex2f(x1, y1)
                glVertex2f(x2, y2)
            glEnd()
    for name in bodies.keys():
        body = bodies[name]
        x, y = pixPos(bodies, body.p) - np.array((body.r, body.r)) * SIZE // 2
        #print('Le coordinate di ' + name + ' sono ' + str(x) + ',' + str(y))
        sprite = pyglet.sprite.Sprite(body.img, x, y)
        sprite.update(scale = body.r)
        sprite.draw()
    update()
    frames += 1
@window.event
def on_mouse_motion(x, y, dx, dy):
    global dt
    dt = min(np.linalg.norm(np.array((dx, dy))), dt_start)

pyglet.app.run()

'''
Aggiungi:
    verifica collisione(con raggio vero)
    
'''
            



"""
Solar System Simulator

Created on Sat Oct 31 12:46:34 2020

Initial Condition at ?

@author: robins
"""

import numpy as np
import random as rd
import pyglet
from pyglet.gl import *
from pyglet.window import key
from pyglet.window import FPSDisplay
import buttonsLib as bt


names = ['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']

class Body:
    def __init__(self, m, r, p, pDot, name=False, color=(255, 255, 255, 255)):
        self.name = name
        self.img = pyglet.resource.image(name + '.png') if name in names else pyglet.resource.image('Jupiter.png')
        self.r = r
        self.m = m
        self.p = np.array(p)
        self.pDot = np.array(pDot)
        self.color = color
        
def kmToUA(x):
    return x / 149597870.69  

def massCenter(bodies):
    c = np.array((0.,0.))
    den = 0
    for name in bodies.keys():
        den += bodies[name].m
        c += bodies[name].m * bodies[name].p
    return c / den

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

def collision(bodies):
    global collisionsText
    names = list(bodies.keys())
    collisions = []
    for i in range(len(names)):
        for j in range(i+1,len(names)):
            bi, bj = bodies[names[i]], bodies[names[j]]
            if bi.m <= bj.m:
                bi, bj = bj, bi
            radSum = bi.r + bj.r
            distCent = np.linalg.norm(bi.p - bj.p)
            if distCent < radSum:
                collisions += [[bi, bj]]
    for coll in collisions:
        bodies.pop(coll[1].name)
        bodies[coll[0].name].pDot = (coll[0].m * coll[0].pDot + coll[1].m * coll[1].pDot) / (coll[0].m + coll[1].m)
        #collisionsText += [pyglet.text.Label(coll[0].name + ' ha inglobato ' + coll[1].name,font_size=24,x = 2 * WIDTH // 3, y = HEIGHT - 32 * len(collisionText))]
   
def startRandom(n, speed = True):
    global bodies
    bodies = {}
    for i in range(n):
        m = rd.randint(1,100000)
        r = rd.randint(1,100) / 10000
        p = np.array((float(rd.randint(1, 1000)) / 1000, float(rd.randint(1, 1000)) / 100))
        if speed:
            pDot = np.array((rd.randint(1,10) / 100, rd.randint(1,10) / 100))
        else:
            pDot = np.array((0.,0.))
        bodies[str(i)] = Body(m, r, p, pDot, str(i))        
        
def update(Dt):
    global bodies, T, dt, reset, orbits, scaleFactor, buttons, collisionsText
    buttons.update()
    if reset:
        startRandom(10, speed=False)
        reset = False
        scaleFactor = (0.5 * HEIGHT - MARGIN) // maxDistCenter(bodies)
        orbits = {}
        for name in bodies.keys():
            orbits[name] = []
        collisionsText = []
        T = 0
    else:
        #collision(bodies)
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
            
            if realOrbits:
                if orbits[name] == [] or np.linalg.norm(bodies[name].p - orbits[name][-1]) > deltaXReal:
                    orbits[name] += [bodies[name].p]
            else:
                if orbits[name] == [] or np.linalg.norm(pixPos(bodies, bodies[name].p) - orbits[name][-1]) > deltaX:
                    orbits[name] +=[(pixPos(bodies, bodies[name].p))]
            if len(orbits[name]) > memory_steps:
                orbits[name] = orbits[name][1:len(orbits[name]) + 1]

def maxDistCenter(bodies):
    d = 0.001
    cent = massCenter(bodies) if center == 'CenterOfMass' else bodies[center].p
    for name in bodies.keys():
        d = max(d, np.linalg.norm(cent - bodies[name].p))
        #d = max(d, abs(cent[1] - bodies[name].p[1]))
    return d

def maxSize(bodies):
    d = 0
    for name in bodies.keys():
        d = max(d, bodies[name].r)
    return d

def scaled(x):
    return x ** (1 / scale)

def pixPos(bodies, p):
    #trasformazione affine
    adj = massCenter(bodies) if center == 'CenterOfMass' else bodies[center].p
    q = np.array(p) - adj
    return q * scaleFactor + MID_POINT

def realPos(bodies, p):
    #trasformazione affine
    q = np.array(p) - MID_POINT
    return q / scaleFactor

def angle(v):
    '''
    Return a value in (-180, 180].
    '''
    z = v[0] + v[1] * 1j
    return int(np.angle(z, deg = True))


def drawField(bodies, nx= 20, ny = 12):
    #Non funziona
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
            x, y = i * dx, j * dy
            #raw += [direction]
            alpha = angle(direction)
            raw += [alpha]
            module = np.linalg.norm(direction)
            #print(alpha)
            sprite = pyglet.sprite.Sprite(arrow, x - dx // (2 * SIZE), y - dy // (2 * SIZE))
            sprite.update(scale = 0.5 * min(1, 100000 * module), rotation = -alpha)
            sprite.draw()
        fieldData += [raw]
    fieldData = np.array(fieldData)
    fieldData.transpose()
        
bodiesStart = {
            'Sun' :     Body(332950,    kmToUA(696340),     (0., kmToUA(0)),            (0.0000, 0.00000),      'Sun',      (255, 200, 0, 0.8)),
            'Mercury' : Body(0.0553,    kmToUA(2439.64),    (0., kmToUA(57909175)),     (0.0080, -0.00001),     'Mercury',  (223, 16, 28, 0.8)),
            'Venus' :   Body(0.815,     kmToUA(6051.59),    (0., kmToUA(108208930)),    (0.0060, 0.00002),      'Venus',    (210, 141, 0, 0.8)),
            'Earth' :   Body(1,         kmToUA(6378.15),    (0., kmToUA(149598262)),    (0.0050, 0.00000),      'Earth',    (0, 135, 255, 0.8)),
            'Mars' :    Body(0.1074,    kmToUA(3397.00),    (0., kmToUA(227936640)),    (0.0040, -0.000012),    'Mars',     (169, 63, 28, 0.8)),
            'Jupiter' : Body(318,       kmToUA(71492.6),    (0., kmToUA(778412010)),    (0.0020, -0.0002),      'Jupiter',  (100, 70, 0, 0.8)),
            'Saturn' :  Body(95.1608,   kmToUA(60267.1),    (0., kmToUA(1426725400)),   (0.0015, 0.00017),      'Saturn',   (239, 166, 0, 0.8)),
            'Uranus' :  Body(14.5357,   kmToUA(25557.25),   (0., kmToUA(2870972200)),   (0.0010, 0.000011),     'Uranus',   (0, 200, 150, 0.8)),
            'Neptune' : Body(17.148,    kmToUA(24766.36),   (0., kmToUA(4498252900)),   (0.0008, 0.000000),     'Neptune',  (0, 166, 220, 0.8))
        } 
bodies = bodiesStart.copy()   
fieldData = []
collisionsText = []
orbits = {}
for name in bodies.keys():
    orbits[name] = []
#settings
G = 6.67 * 10 ** -11 #costante gravitazione universale
dt = 1 #passo di interpolazione dati
dt_start = 0.1 #passo di interpolazione dei dati iniziale, nonché massimo
center = 'CenterOfMass' #Punto che vine visulizzato il centro dello schermo. Try 'CenterOfMass'
deltaXReal = 0.1 #passo di interpolazione lineare nella visualizzazione delle orbite in UA
deltaX = 8 #passo di interpolazione lineare nella visualizzazione delle orbite in pixels
memory_steps = 100 #WQuanti segmenti costituenti le orbite compiute tenere in memoria
scale = 6 # Significa che i raggi dei pianeti saranno rappresentati in scala radicale con inidice 'scale'
maxPix = 5 #the larger body will measure maxPix pixels of radius
centerChanged = False
viewOrbits = True
viewField = False
autoScale = False
realOrbits = False

T = 0 #tempo corrente
SIZE = 256 #dimensione dello sprite quadrato dei pianeti / corpi
window = pyglet.window.Window(fullscreen = True)
fps_display = FPSDisplay(window)
WIDTH, HEIGHT = window.get_size()
MARGIN = 32
MID_POINT = np.array((WIDTH // 2, HEIGHT // 2))
reset = False

scaleFactor = (0.5 * HEIGHT - MARGIN) // maxDistCenter(bodies)
sizeBodiesFactor = maxPix * HEIGHT / (scaled(maxSize(bodies)) * SIZE)

#Buttons
'''init of Button: (self, text, save, update, info='',kind='none', value=0, x=0, y=0, binValues = [0, 1])'''

def save1(x):
    global dt_start; dt_start = x
def save2(x):
    global center, orbits, centerChanged; center = x; centerChanged = True
    for name in orbits.keys():
        orbits[name] = []
def save3(x):
    global scale; scale = x
def save4(x):
    global maxPix, sizeBodiesFactor; maxPix = x; sizeBodiesFactor = maxPix * HEIGHT / (scaled(maxSize(bodies)) * SIZE)
def save5(x):
    global deltaX; deltaX = x
def save6(x):
    global memory_steps; memory_steps = x
def save7(x):
    global viewOrbits; viewOrbits = x
def save8(x):
    global viewField; viewField = x
def save9(x):
    global autoScale; autoScale = x
def save10(x):
    global scaleFactor, sizeBodiesFactor; r = scaleFactor / x; scaleFactor = x; sizeBodiesFactor /= r
def save11(x):
    global realOrbits, orbits; realOrbits = x; orbits = {}
    for name in bodies.keys():
        orbits[name] = []
def restartAct():
    global reset; reset = True
def notAct(x):
    pass

def up1(b):
    b.value = dt_start
def up2(b):
    b.value = center
def up3(b):
    b.value = scale
def up4(b):
    b.value = maxPix
def up5(b):
    b.value = deltaX
def up6(b):
    b.value = memory_steps
def up7(b):
    b.value = viewOrbits
def up8(b):
    b.value = viewField
def up9(b):
    b.value = autoScale
def up10(b):
    b.value = scaleFactor
def up11(b):
    b.value = realOrbits
def upR(b):
    pass

info1 = ['MUST BE a natural Number.',
         'Is the magnitude of maximum dt used in interpolation of motion laws.', 
         'An high value imply more velocity of evolution but an higher interpolation error.']
info2 = ['The system will be represented fixid \'Center Name\' as a center.', 
         'The value MUST BE one of the following:', 
         '        CenterOfMass', '        Sun', '        Mercury', '        Venus', '        Earth', 
         '        Mars', '        Jupiter', '        Saturn', '        Uranus', '        Neptune']
info3 = ['MUST BE a natural number. Suggested in {1, ... , 10}.',
         'Represent the power of the radical scale in to which planets diameters are represented.']
info4 = ['MUST BE a natural number.',
         'Represent the number of pixels of radius of the larger body in the system.']
info5 = ['MUST BE a natural number.',
         'Represent the size of the segments made to approximate the orbits.']
info6 = ['MUST BE a natural number.',
         'Represent how many segments (of \'Orbits step\' pixels) made every orbit.']
info7 = ['Click to change value (True or False)',
         '        If True: orbits will be shown.',
         '        Else, not.']
info8 = ['Click to change value (True or False)',
         '        If True: gravitation field will be shown.',
         '        Else, not.']
info9 = ['Click to change value (True or False)',
         '        If True: Every frame refresh scale of image view will be recalculate',
         '                 to see all bodie in the screen.',
         '        Else, not.',
         'Attenction: a True value can obstacle the intuitive view of orbits']
info10 = ['Represent the inverse of zoom with you wan to view the system.', 
          'This means that with an high (low) value you\'ll see the system by far (near)',
          'By Default it is good to view all bodies as large as possible.',
          'It not changable if mode \'Auto Scale\' is active.']
info11 = ['Click to change value (True or False)',
          '        If True: The orbits are shown in a inertial reference system.',
          '                 Recomanded if mode \'Auto Scale\' is active',
          '        Else, the orbits are shown in a reference system supportive to the center.']
infoR = ['Restart the simulation.']

b1 = bt.Button('Max Speed',     save1,      up1,    info1,  'insert',       dt_start)
b2 = bt.Button('Center Name',   save2,      up2,    info2,  'insert',       center)
b3 = bt.Button('Scale',         save3,      up3,    info3,  'insert',       scale)
b4 = bt.Button('Bodies Size',   save4,      up4,    info4,  'insert',       maxPix)
b5 = bt.Button('Orbits step',   save5,      up5,    info5,  'insert',       deltaX)
b6 = bt.Button('Length Orbits', save6,      up6,    info6,  'insert',       memory_steps)
b7 = bt.Button('View Orbits',   save7,      up7,    info7,  'click',        viewOrbits)
b8 = bt.Button('View Field',    save8,      up8,    info8,  'click',        viewField)
b9 = bt.Button('Auto Scale',    save9,      up9,    info9,  'click',        autoScale)
b10 = bt.Button('Back Zoom',    save10,     up10,   info10, 'insert',       scaleFactor)
b11 = bt.Button('Real Orbits',  save11,     up11,   info11, 'click',        realOrbits)
restartB = bt.Button('Reset',   restartAct, upR,    infoR,  'singleAction', reset)
buttons = bt.Buttons([b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, restartB], WIDTH, HEIGHT)

#from pyglet.window import mouse
keys = key.KeyStateHandler()
window.push_handlers(keys)

@window.event
def on_draw():
    window.clear()
    global scaleFactor, centerChanged, sizeBodiesFactor
    if centerChanged or autoScale:
        x = (0.5 * HEIGHT - MARGIN) // maxDistCenter(bodies)
        r = scaleFactor / x; scaleFactor = x; sizeBodiesFactor /= r
        centerChanged = False
    fps_display.draw()
    timeText = pyglet.text.Label('Time: ' + str(T),font_size=24, x=2 * WIDTH // 3, y=bt.margin)
    timeText.draw()
    for txt in collisionsText:
        txt.draw()
    if viewField:    
        drawField(bodies, 20, 10)
    if viewOrbits:
        for name in bodies.keys():
            if len(orbits[name]) > 1:
                glBegin(GL_LINES)
                (r, g
                 , b, a) = np.array(bodies[name].color) / 255
                glColor4f(r, g, b, a)
                for i in range(0,len(orbits[name])-1):
                    # create a line, x,y
                    if realOrbits:
                        x1, y1 = pixPos(bodies, orbits[name][i])
                        x2, y2 = pixPos(bodies, orbits[name][i+1])
                    else:
                        x1, y1 = orbits[name][i]
                        x2, y2 = orbits[name][i+1]
                    glVertex2f(x1, y1)
                    glVertex2f(x2, y2)
                glEnd()
    for name in bodies.keys():
        body = bodies[name]
        x, y = pixPos(bodies, body.p) - np.array((scaled(body.r), scaled(body.r))) * max(sizeBodiesFactor, 10 / SIZE)
        #print('Le coordinate di ' + name + ' sono ' + str(x) + ',' + str(y))
        sprite = pyglet.sprite.Sprite(body.img, x, y)
        sprite.update(scale = max((2 * sizeBodiesFactor * scaled(body.r)) / SIZE, 2 / SIZE))
        sprite.draw()
    buttons.draw()

@window.event
def on_mouse_motion(x, y, dx, dy):
    global dt
    dt = min(np.linalg.norm(np.array((dx, dy))), dt_start)
    for i in range(len(buttons.buttons)):
        b = buttons.buttons[i]
        if i == 0 or bt.show:
            if b.isSelected(x, y):
                b.selected = True
            else:
                b.selected = False
            
@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.SPACE:
        global dt
        dt = 0 if dt > 0 else dt_start
    for b in buttons.buttons:
        if b.writing:
            if modifiers & key.MOD_SHIFT:
                b.insert(symbol + 1000)
            else:
                b.insert(symbol)
            
@window.event
def on_mouse_press(x, y, button, modifiers):
    for i in range(len(buttons.buttons)):
        b = buttons.buttons[i]
        if i == 0 or bt.show:        
            if b.isSelected(x, y):
                if button & pyglet.window.mouse.LEFT:
                    b.click()
                elif button & pyglet.window.mouse.RIGHT:
                    b.rightClick()

# if __name__ == '__main__':
pyglet.clock.schedule_interval(update, 1. / 60.)
pyglet.app.run()
    
'''
Aggiungi:
    Gestisci collisione (conservazione quantità di moto)
    Scegli se visualizzare graficamente il vettore velocità applicato ad ogni corpo
    Aggiusta la visualizzazione campo
    Sposta posizione e velocità dai corpi con il Mouse (mentre lo vai visualizza i dati scritti sullo schermo)
    CONTROLLA LE UNITà DI MISURAAAAA!!!
'''

'''
Dati reali Sistema solare  con config iniziale allineata (eccezion fatta per le velocità)
bodies = {
            'Sun' :     Body(332950,    kmToUA(696340),     (0., kmToUA(0)),            (0.0000, 0.00000),      'Sun',      (255, 200, 0, 0.8)),
            'Mercury' : Body(0.0553,    kmToUA(2439.64),    (0., kmToUA(57909175)),     (0.0080, -0.00001),     'Mercury',  (223, 16, 28, 0.8)),
            'Venus' :   Body(0.815,     kmToUA(6051.59),    (0., kmToUA(108208930)),    (0.0060, 0.00002),      'Venus',    (210, 141, 0, 0.8)),
            'Earth' :   Body(1,         kmToUA(6378.15),    (0., kmToUA(149598262)),    (0.0050, 0.00000),      'Earth',    (0, 135, 255, 0.8)),
            'Mars' :    Body(0.1074,    kmToUA(3397.00),    (0., kmToUA(227936640)),    (0.0040, -0.000012),    'Mars',     (169, 63, 28, 0.8)),
            'Jupiter' : Body(318,       kmToUA(71492.6),    (0., kmToUA(778412010)),    (0.0020, -0.0002),      'Jupiter',  (100, 70, 0, 0.8)),
            'Saturn' :  Body(95.1608,   kmToUA(60267.1),    (0., kmToUA(1426725400)),   (0.0015, 0.00017),      'Saturn',   (239, 166, 0, 0.8)),
            'Uranus' :  Body(14.5357,   kmToUA(25557.25),   (0., kmToUA(2870972200)),   (0.0010, 0.000011),     'Uranus',   (0, 200, 150, 0.8)),
            'Neptune' : Body(17.148,    kmToUA(24766.36),   (0., kmToUA(4498252900)),   (0.0008, 0.000000),     'Neptune',  (0, 166, 220, 0.8))
        } 
Dati visibilmente apprezzabili
{
        'Sun' :     Body(332950,    kmToUA(696340),     (0., 0.),       (0.0000, 0.00000),      'Sun',      (255, 200, 0, 0.8)),
        'Mercury' : Body(0.0553,    kmToUA(2439.64),    (0., 0.33),     (0.0080, -0.00001),     'Mercury',  (223, 16, 28, 0.8)),
        'Venus' :   Body(0.815,     kmToUA(6051.59),    (0., 0.66),     (0.0060, 0.00002),      'Venus',    (210, 141, 0, 0.8)),
        'Earth' :   Body(1,         kmToUA(6378.15),    (0., 1.00),     (0.0050, 0.00000),      'Earth',    (0, 135, 255, 0.8)),
        'Mars' :    Body(0.1074,    kmToUA(3397.00),    (0., 1.33),     (0.0040, -0.000012),    'Mars',     (169, 63, 28, 0.8)),
        'Jupiter' : Body(318,       kmToUA(71492.6),    (0., 1.66),     (0.0040, -0.000010),    'Jupiter',  (100, 70, 0, 0.8)),
        'Saturn' :  Body(95.1608,   kmToUA(60267.1),    (0., 2.00),     (0.0032, 0.000017),     'Saturn',   (239, 166, 0, 0.8)),
        'Uranus' :  Body(14.5357,   kmToUA(25557.25),   (0., 2.33),     (0.0031, 0.000011),     'Uranus',   (0, 200, 150, 0.8)),
        'Neptune' : Body(17.148,    kmToUA(24766.36),   (0., 2.66),     (0.0028, 0.000000),     'Neptune',  (0, 166, 220, 0.8))
        }   
'''

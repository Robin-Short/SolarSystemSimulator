import pyglet

window = pyglet.window.Window()
i = 0

@window.event
def on_draw():
    global i
    window.clear()
    label = pyglet.text.Label('Prova ' + str(i))
    label.draw()
    i += 1

pyglet.app.run()
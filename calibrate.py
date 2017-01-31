import pyglet
from pyglet.window import mouse
import sys
import pyft_config
from pyglet.window import key
from math import sqrt

def writeCalibrationFile(xs,ys):
    dx = xs[1] - xs[0]
    dy = ys[1] - ys[0]
    dist = sqrt(dx**2.0 + dy**2.0)
    dpi = round(dist/3.0)
    fid = open(pyft_config.CALIBRATION_FILENAME,'w')
    fid.write('%d'%int(dpi))
    fid.close()
    print 'calibrated dpi:',dpi
    sys.exit('Exiting normally.')

window = pyglet.window.Window(fullscreen=False)
display = window.display
screens = display.get_screens()

iScreen = pyft_config.TARGET_DEFAULT_SCREEN


try:
    screen = screens[iScreen]
except IndexError:
    print 'Current display has only', len(screens), 'screen, but DEFAULT_SCREEN is set to',pyft_config.TARGET_DEFAULT_SCREEN,'in pyft_config.py.'
    sys.exit()

fullScreen = True
window.set_fullscreen(fullScreen,screen)

width = window.width
height = window.height


label = pyglet.text.Label('Please click two points separated by 3in (the edge of a common post-it note).',
                          font_name=pyft_config.FONT_NAME,
                          font_size=pyft_config.FONT_SIZE,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

xs = []
ys = []

@window.event
def on_draw():
    window.clear()
    label.draw()

@window.event
def on_mouse_release(x,y,button,modifiers):
    xs.append(x)
    ys.append(y)
    if len(xs)==2:
        writeCalibrationFile(xs,ys)

@window.event
def on_key_press(symbol,modifiers):
    global iScreen,screens,window,height,width
    if symbol==key.ENTER:
        if fullScreen:
            iScreen = (iScreen+1)%len(screens)
            window.set_fullscreen(True,screens[iScreen])
            height = window.height
            width = window.width

        
pyglet.app.run()

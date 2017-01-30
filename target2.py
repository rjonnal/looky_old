import pyglet
#from pyglet.gl import *
import sys,os,datetime,math
import config
from pyglet.window import key
from time import sleep,time
import Tkinter, tkFileDialog, tkSimpleDialog

class FixationTargetApp:
    '''This class represents the entire application. All Target
    objects are properties of this class. Also, this class owns all
    OpenGL objects, so it's responsible for making sure a context
    exists for drawing them, etc.
    '''
    def __init__(self):

        root = Tkinter.Tk()
        root.withdraw()
        self.console = Console()

        self.useFundusImage = config.USE_FUNDUS_IMAGE

        # set up the main (target) window and get its display and screens
        self.targetWindow = pyglet.window.Window(fullscreen=False)
        self.targetDisplay = self.targetWindow.display
        self.targetScreens = self.targetDisplay.get_screens()
        self.iTargetScreen = config.TARGET_DEFAULT_SCREEN

        self.console.disp('target window: %d screen(s) detected'%len(self.targetScreens))
        for screen in self.targetScreens:
            self.console.disp('\t %s'%screen)

        # if a fundus image is to be used in conjunction with the target
        if self.useFundusImage:
            self.fundusWindow = pyglet.window.Window(fullscreen=False)
            self.fundusDisplay = self.fundusWindow.display
            self.fundusScreens = self.fundusDisplay.get_screens()
            self.iFundusScreen = config.FUNDUS_DEFAULT_SCREEN
            self.console.disp('fundus window: %d screen(s) detected'%len(self.targetScreens))
            for screen in self.targetScreens:
                self.console.disp('\t %s'%screen)

        # try to use the physical screen specified in config.py
        try:
            self.targetScreen = self.targetScreens[self.iTargetScreen]
            self.console.disp('target: using screen %s'%self.targetScreen)
#             print 'Using screen',self.iTargetScreen
        except IndexError:
            print 'config.TARGET_DEFAULT_SCREEN is too high. Remember that screens are numbered starting with 0.'
            sys.exit()

        # set up window for fundus image, if it's in use
        if self.useFundusImage:
            try:
                self.fundusScreen = self.fundusScreens[self.iFundusScreen]
                self.console.disp('fundus: using screen %s'%self.fundusScreen)
    #             print 'Using screen',self.iTargetScreen
            except IndexError:
                print 'config.FUNDUS_DEFAULT_SCREEN is too high. Remember that screens are numbered starting with 0.'
                sys.exit()

        # a bit awkward, but even if we want to start up w/o fullscreen, we
        # need to make the target screen fullscreen in order to determine
        # its size, get the width and height, and position things accordingly
        self.targetFullScreen = True
        self.targetWindow.set_fullscreen(self.targetFullScreen,self.targetScreen)

        self.targetWindowWidth = self.targetWindow.width
        self.targetWindowHeight = self.targetWindow.height

        if self.useFundusImage:
            self.fundusWindowWidth = self.fundusWindow.width
            self.fundusWindowHeight = self.fundusWindow.height

        # set the OpenGL clearing color, specified in config.py
        pyglet.gl.glClearColor(config.BACKGROUND_COLOR[0],config.BACKGROUND_COLOR[1],config.BACKGROUND_COLOR[2],1.0)

        # instantiate a visual angle to pixel converter object:
        converter = Converter(self.targetWindow)

        # instantiate a retinal location object
        loc = RetinalLocation(converter,self.targetWindow)

        # instantiate a logger and pass it to the RetinalLocation object,
        # so that the RetinalLocation object can log its own position as
        # needed
        self.logger = Logger(loc)
        loc.setLogger(self.logger)

        # if we're using a fundus image, we need to prompt the user to enter
        # the location of the image, using a simple Tk UI widget; unfortunately,
        # if the target window is full screen, the Tk widget isn't immediately
        # visible, so we un-fullscreen the target window, load the fundus image,
        # and then fullscreen the target window again:
        if self.useFundusImage:
            self.targetWindow.set_fullscreen(False,self.targetScreen)
            self.fi = FundusImage(loc,self.fundusWindow,self.logger,self.console)
            self.targetWindow.set_fullscreen(True,self.targetScreen)
            # resize the fundus window to match the size of the fundus image;
            # note that currently there's no way to scale down a fundus image;
            # if it's larger than the monitor resolution, this will be an annoying
            # problem
            fiwidth,fiheight = self.fi.getImageSize()
            self.fundusWindow.set_size(fiwidth,fiheight)

        # use pyglet's scheduler to automatically log the target's status:
        pyglet.clock.schedule_interval(self.logger.log,config.LOGGING_PERIOD)

        # make a keys object to handle keystrokes and print help
        self.keys = Keys(self.console,self.logger)

        # instantiate the target object
        target = BlinkyStar(config.DEFAULT_LINE_WIDTH_DEG,config.DEFAULT_TARGET_RADIUS_DEG)
        
        def nextScreen():
            '''A function for switching physical screens.
            '''
            if self.targetFullScreen:
                self.iTargetScreen = (self.iTargetScreen+1)%len(self.targetScreens)
                self.console.disp('switching to screen %d'%self.iTargetScreen)
                self.targetWindow.set_fullscreen(True,self.targetScreens[self.iTargetScreen])
                self.targetWindowHeight = self.targetWindow.height
                self.targetWindowWidth = self.targetWindow.width

        def toggleFullScreen():
            self.targetFullScreen = not self.targetFullScreen
            self.targetWindow.set_fullscreen(self.targetFullScreen,self.targetScreens[self.iTargetScreen])

        def showFPS():
            '''Show the FPS of the application; note this is not OpenGL's FPS.
            '''
            self.console.disp('drawing at %0.2f fps'%(self.nFrames/self.dt))

        # associate keyboard keys with functions, key descriptions, and help blurbs
        self.keys.section('Main target movements')
        self.keys.add(key.UP,0,loc.moveUp,'up arrow','move target up by %0.1f deg'%config.RETINA_UNIT_DEG)
        self.keys.add(key.RIGHT,0,loc.moveRight,'right arrow','move target right by %0.1f deg'%config.RETINA_UNIT_DEG)
        self.keys.add(key.LEFT,0,loc.moveLeft,'left arrow','move target left by %0.1f deg'%config.RETINA_UNIT_DEG)
        self.keys.add(key.DOWN,0,loc.moveDown,'down arrow','move target down by %0.1f deg'%config.RETINA_UNIT_DEG)
        self.keys.section('Alternate target movements')
        self.keys.add(key.UP,key.MOD_CTRL,loc.moveUpAlt,'ctrl up arrow','move target up by %0.1f deg'%config.RETINA_ALTERNATE_UNIT_DEG)
        self.keys.add(key.RIGHT,key.MOD_CTRL,loc.moveRightAlt,'ctrl right arrow','move target right by %0.1f deg'%config.RETINA_ALTERNATE_UNIT_DEG)
        self.keys.add(key.LEFT,key.MOD_CTRL,loc.moveLeftAlt,'ctrl left arrow','move target left by %0.1f deg'%config.RETINA_ALTERNATE_UNIT_DEG)
        self.keys.add(key.DOWN,key.MOD_CTRL,loc.moveDownAlt,'ctrl down arrow','move target down by %0.1f deg'%config.RETINA_ALTERNATE_UNIT_DEG)
        self.keys.section('Target center offset')
        self.keys.add(key.O,0,loc.brieflyShowOffset,'o','show offset info')
        self.keys.add(key.UP,key.MOD_ALT,loc.increaseYOffset,'alt up arrow','move offset up by %d pixels'%config.OFFSET_UNIT_PIXELS)
        self.keys.add(key.RIGHT,key.MOD_ALT,loc.increaseXOffset,'alt right arrow','move offset right by %d pixels'%config.OFFSET_UNIT_PIXELS)
        self.keys.add(key.LEFT,key.MOD_ALT,loc.decreaseXOffset,'alt left arrow','move offset left by %d pixels'%config.OFFSET_UNIT_PIXELS)
        self.keys.add(key.DOWN,key.MOD_ALT,loc.decreaseYOffset,'alt down arrow','move offset down by %d pixels'%config.OFFSET_UNIT_PIXELS)
        self.keys.section('Target size/shape')
        self.keys.add(key.EQUAL,0,target.increaseRadius,'=','increase target radius by %0.1f deg'%config.TARGET_RADIUS_UNIT)
        self.keys.add(key.MINUS,0,target.decreaseRadius,'-','decrease target radius by %0.1f deg'%config.TARGET_RADIUS_UNIT)
        self.keys.add(key.EQUAL,key.MOD_CTRL,target.increaseLineWidth,'ctrl =','increase target line width by %0.2f deg'%config.LINE_WIDTH_UNIT)
        self.keys.add(key.MINUS,key.MOD_CTRL,target.decreaseLineWidth,'ctrl -','decrease target line width by %0.2f deg'%config.LINE_WIDTH_UNIT)
        self.keys.add(key.EQUAL,key.MOD_ALT,target.increaseBlinkPeriod,'alt =','increase target blink period by %0.1f percent'%(config.BLINK_PERIOD_ADJUSTMENT_FACTOR*100.0))
        self.keys.add(key.MINUS,key.MOD_ALT,target.decreaseBlinkPeriod,'alt -','decrease target blink period by %0.1f percent'%(config.BLINK_PERIOD_ADJUSTMENT_FACTOR*100.0))
        self.keys.section('Other')
        self.keys.add(key.SPACE,0,loc.switchEye,'space','switch eye')
        self.keys.add(key.ENTER,0,nextScreen,'enter','next screen')
        self.keys.add(key.F5,0,toggleFullScreen,'f5','toggle full screen')
        self.keys.add(key.C,0,self.console.toggleVisible,'c','toggle console')
        self.keys.add(key.F,key.MOD_SHIFT,showFPS,'F','show fps')
        self.keys.add(key.G,0,loc.toggleGrid,'g','toggle target grid')
        if self.useFundusImage:
            self.keys.add(key.H,0,self.fi.toggleGrid,'h','toggle fundus grid')
        self.keys.add(key.ESCAPE,0,sys.exit,'esc','quit')
        self.keys.section('Help')
        self.keys.add(key.QUESTION,key.MOD_SHIFT,self.keys.toggleHelp,'?','show/hide help')

        self.t0 = time()
        self.nFrames = 0.0
        
        # we have several objects that want to draw to the screen (the target, the retinal location, the keys
        # want to draw their help message, the console wants to draw it's output, etc. these are all called here:
        @self.targetWindow.event
        def on_draw():
            pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
            target.draw(loc.xPx(),loc.yPx())
            loc.draw(self.targetWindowWidth,self.targetWindowHeight)
            self.keys.draw(5,self.targetWindowHeight)
            self.console.draw()
            self.nFrames+=1
            self.dt = time() - self.t0
            
        # if a key is pressed, simply pass it on to the keys object
        @self.targetWindow.event
        def on_key_press(symbol,modifiers):
            self.keys.command(symbol,modifiers)

        if self.useFundusImage:
            @self.fundusWindow.event
            def on_key_press(symbol,modifiers):
                self.keys.command(symbol,modifiers)

            @self.fundusWindow.event
            def on_draw():
                pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
                self.fi.draw()

            # the target is positionable by mouse clicks on the fundus image,
            # so we need a mouse listener for the fundusWindow
            # it should listen to three kinds of events:
            # 1. ctrl-click, which selects the PRL
            # 2. shift-ctrl-click, which selects the edges of the image and
            #    allows the user to enter a scale in visual angle
            # 3. click, which moves the target around
            @self.fundusWindow.event
            def on_mouse_release(x,y,buttons,modifiers):
                if (modifiers&key.MOD_SHIFT)and(modifiers&key.MOD_CTRL):
                    self.fi.toggleSettingScale(x,y)
                elif (modifiers&key.MOD_CTRL):
                    self.fi.setPRL(x,y)
                elif (modifiers&key.MOD_SHIFT):
                    self.fi.chooseLocation(x,y,False)
                else:
                    self.fi.chooseLocation(x,y)

        pyglet.app.run()
        self.logger.close()

class Converter:
    '''Converts visual angles to screen pixels.'''
    def __init__(self,window):
        self.dpi = self.loadDpi()
        self.plateScaleRadPerM = config.PLATE_SCALE_RAD_PER_M
        self.dpi = self.loadDpi()
        self.pi = math.pi
        self.xoff = window.width/2.0
        self.yoff = window.height/2.0

    def d2p(self,angleDeg):
        mPerPx = .0254/self.dpi
        degPerRad = 180.0/self.pi
        psDegPerPx = self.plateScaleRadPerM * mPerPx * degPerRad
        return angleDeg/psDegPerPx

    def loadDpi(self):
        fn = config.CALIBRATION_FILENAME
        fn = os.path.abspath('.')+'/'+fn
        fid = open(fn,'r')
        dpistr = fid.readline().strip()
        fid.close()
        return float(dpistr)
        
    def getXoff(self):
        return self.xoff

    def getYoff(self):
        return self.yoff

class Grid:
    '''Represents a grid of x- and y- locations. Provides methods for
    generating locations (given a center and spacing), shifting 
    locations, and drawing the grid.
    '''
    def __init__(self,x0,y0,width,height,spacing,centerColor,otherColor,style='points',size=1.0,border=config.DEFAULT_GRID_BORDER):
        self.x0 = x0
        self.y0 = y0
        self.width = width
        self.height = height
        self.border = border
        self.xLoci = self.makeLoci(x0,width,spacing)
        self.yLoci = self.makeLoci(y0,height,spacing)
        self.cc = centerColor
        self.oc = otherColor
        self.style = style
        self.size = size
        self.spacing = spacing
        self.vertexList,self.N = self.makeVertexList(style)

    def makeLoci(self,center,length,spacing):
        loci = []
        locus = center
        border = self.border
        while locus >= -border:
            loci.append(locus)
            locus = locus - spacing
        loci.reverse()
        locus = center + spacing
        while locus < length + border:
            loci.append(locus)
            locus = locus + spacing
        return loci


    def shift(self,dim,px):
        for n in range(self.N):
            self.vertexList.vertices[n*2+dim] = self.vertexList.vertices[n*2+dim]+px

    def xShift(self,px):
        self.shift(0,px)
        
    def yShift(self,px):
        self.shift(1,px)

    def makeVertexList(self,style):
        vertexList = None
        n = 0
        if style.lower()=='points':
            vlist = []
            clist = []
            for x in self.xLoci:
                for y in self.yLoci:
                    vlist.append(x)
                    vlist.append(y)
                    if x==self.x0 or y==self.y0:
                        clist = clist + self.cc
                    else:
                        clist = clist + self.oc
                    n+=1

        if style.lower()=='pluses':
            vlist = []
            clist = []
            rad = self.size/2.0
            for x in self.xLoci:
                for y in self.yLoci:
                    vlist = vlist + [x-rad,y,x+rad,y,x,y+rad,x,y-rad]
                    if x==self.x0 or y==self.y0:
                        clist = clist + self.cc*4
                    else:
                        clist = clist + self.oc*4
                    n+=4
            

        if style.lower()=='graph':
            vlist = []
            clist = []
            top = max(self.yLoci)
            bottom = min(self.yLoci)
            left = min(self.xLoci)
            right = max(self.xLoci)
            for x in self.xLoci:
                vlist = vlist + [x,top,x,bottom]
                if x==self.x0:
                    clist = clist + self.cc*2
                else:
                    clist = clist + self.oc*2
                n+=2
            for y in self.yLoci:
                vlist = vlist + [left,y,right,y]
                if y==self.y0:
                    clist = clist + self.cc*2
                else:
                    clist = clist + self.oc*2
                n+=2
                
                
        vertexList = pyglet.graphics.vertex_list(n,('v2f',vlist),('c3f',clist))
        return vertexList,n

    def draw(self):
        drawType = pyglet.gl.GL_POINTS
        if self.style.lower()=='points':
            pyglet.gl.glPointSize(self.size)
            drawType = pyglet.gl.GL_POINTS
        if self.style.lower()=='pluses':
            pyglet.gl.glLineWidth(1.0)
            drawType = pyglet.gl.GL_LINES
        if self.style.lower()=='graph':
            pyglet.gl.glLineWidth(1.0)
            drawType = pyglet.gl.GL_LINES
        self.vertexList.draw(drawType)
        

class FundusImage:
    '''Represents a fundus image of the subject being imaged; this class
    loads a fundus image from a file, and presents the image in a second,
    clickable window, which then moves the fixation target accordingly.
    '''
    def __init__(self,retinalLocation,window,logger,console):
        self.loc = retinalLocation
        self.targetWindow = self.loc.window
        self.fundusWindow = window
        self.windows = [self.targetWindow,self.fundusWindow]
        
        self.logger = logger
        self.console = console

        self.partScreen()

        # during design and testing, don't prompt user to select
        # a fundus image; just load the test image
        if config.TESTING:
            self.file = open('./fundus/test.jpg')
            self.fi = pyglet.image.load(self.file.name)
        else:
            self.file = tkFileDialog.askopenfile(mode='r')
            self.fi = pyglet.image.load(self.file.name)


        self.logger.logThis('loading fundus image from %s'%self.file.name)
        self.width = self.fi.width
        self.height = self.fi.height
        self.textPadding = 10
        self.PRLset = False
        self.scaleSet = False
        self.settingScale = False
        self.toMaximize = []
        self.color = [200,0,0,128]
        self.showGrid = False
        self.mgrid = None
        self.Mgrid = None

    def toggleGrid(self):
        self.showGrid = not self.showGrid

    def partScreen(self):
        for window in self.windows:
            if window._fullscreen:
                screen = window._screen
                window.set_fullscreen(False,screen)
                self.toMaximize.append(window)

    def fullScreen(self):    
        for window in self.toMaximize:
            screen = window._screen
            window.set_fullscreen(True,screen)
        self.toMaximize = []

    def getImageSize(self):
        return self.fi.width,self.fi.height

    def chooseLocation(self,x,y,snapToGrid=True):
        if not self.PRLset:
            print 'No PRL set!'
            return
        if not self.scaleSet:
            print 'Scale not set!'
            return
        
        x = -(x - self.PRLx)
        y = y - self.PRLy
        xDeg = x/self.pxPerDeg
        yDeg = y/self.pxPerDeg
        if snapToGrid:
            factor = config.RETINA_ALTERNATE_UNIT_DEG
            xDeg = float(round(xDeg/factor))*factor
            yDeg = float(round(yDeg/factor))*factor
        self.loc.setLocation(xDeg,yDeg)
        self.console.disp('Location set to %0.2f,%0.2f'%(xDeg,yDeg))

    def setPRL(self,x,y):
        self.PRLset = True
        self.PRLx = x
        self.PRLy = y
        self.logger.logThis('setting fundus image PRL to x=%d, y=%d'%(x,y))
        self.makeGrid()
        
    def toggleSettingScale(self,x,y):
#         print 'toggle',self.settingScale
        if not self.settingScale:
            self.settingScale = True
            self.xstart = x
            self.ystart = y
        else:
            self.xstop = x
            self.ystop = y
            dx = x - self.xstart
            dy = y - self.ystart
            dpx = math.sqrt(dx**2.0 + dy**2.0)
            self.partScreen()
            ddeg = tkSimpleDialog.askfloat('Enter degrees','Please enter corresponding degrees:')
            self.fullScreen()
            self.pxPerDeg = float(dpx)/float(ddeg)
            self.logger.logThis('setting fundus image scale, %0.0f pixels / %0.1f deg =  %0.1f px/deg'%(dpx,ddeg,self.pxPerDeg))
            self.scaleSet = True
            self.settingScale = False
            self.makeGrid()

    def makeGrid(self):
        if self.PRLset and self.scaleSet:
            x0 = self.PRLx
            y0 = self.PRLy
            majorSpacing = config.RETINA_UNIT_DEG*self.pxPerDeg
            minorSpacing = config.RETINA_ALTERNATE_UNIT_DEG*self.pxPerDeg
            self.Mgrid = Grid(x0,y0,self.width,self.height,majorSpacing,config.FUNDUS_GRID_CENTER_COLOR,config.FUNDUS_GRID_MAJOR_COLOR,style='pluses',size=10.0,border=0)
            self.mgrid = Grid(x0,y0,self.width,self.height,minorSpacing,config.FUNDUS_GRID_CENTER_COLOR,config.FUNDUS_GRID_MINOR_COLOR,style='points',size=1.0,border=0)

    def draw(self):
        pyglet.gl.glColor3f(1.0,1.0,1.0)
        self.fi.blit(0,0)
        
        if self.showGrid and not self.mgrid is None:
            self.mgrid.draw()

        if self.showGrid and not self.Mgrid is None:
            self.Mgrid.draw()

        label = pyglet.text.Label(self.loc.info(),
                      font_name=config.FONT_NAME,
                      font_size=config.FONT_SIZE,
                      x=self.width-self.textPadding, y=self.height-self.textPadding,
                      anchor_x='right', anchor_y='top', color=[255,255,255,255])
        label.draw()

        if not self.PRLset:
            label = pyglet.text.Label('No PRL set. CTRL-click to set PRL.',
                          font_name=config.FONT_NAME,
                          font_size=config.FONT_SIZE,
                          x=0+self.textPadding, y=0+self.textPadding+20,
                          anchor_x='left', anchor_y='bottom', color=self.color)
            label.draw()
        if not self.scaleSet:
            label = pyglet.text.Label('No scale set. CTRL-SHIFT-click two points to set scale.',
                          font_name=config.FONT_NAME,
                          font_size=config.FONT_SIZE,
                          x=0+self.textPadding, y=0+self.textPadding,
                          anchor_x='left', anchor_y='bottom', color=self.color)
            label.draw()


class MiniConverter:
    '''Converts visual angles to screen pixels, without keeping
    track of screen offsets; useful for Component objects that need
    to know how to scale themselves using visual angle units but
    don't know anything about the window.
    '''
    def __init__(self):
        self.dpi = self.loadDpi()
        self.plateScaleRadPerM = config.PLATE_SCALE_RAD_PER_M
        self.dpi = self.loadDpi()
        self.pi = math.pi

    def d2p(self,angleDeg):
        mPerPx = .0254/self.dpi
        degPerRad = 180.0/self.pi
        psDegPerPx = self.plateScaleRadPerM * mPerPx * degPerRad
        return angleDeg/psDegPerPx

    def loadDpi(self):
        fn = config.CALIBRATION_FILENAME
        fid = open(fn,'r')
        dpistr = fid.readline().strip()
        fid.close()
        return float(dpistr)

class RetinalLocation:
    '''Keeps track of location of target, performs conversions between
    visual angle and screen pixels.
    '''
    def __init__(self,converter,window):
        self.window = window
        self.width = self.window.width
        self.height = self.window.height
        self.converter = converter
        self.xoff = converter.getXoff()
        self.yoff = converter.getYoff()
        self.makeGrid()
        self.xDeg = 0.0
        self.yDeg = 0.0
        self.eye = config.LEFT
        self.eyeLabels = config.EYE_LABELS
        self.horizontalLabels = config.HORIZONTAL_LABELS
        self.verticalLabels = config.VERTICAL_LABELS
        self.unit = config.RETINA_UNIT_DEG
        self.alternateUnit = config.RETINA_ALTERNATE_UNIT_DEG
        self.xoff0 = self.xoff
        self.yoff0 = self.yoff
        self.textPadding = 10
        self.cross = SimpleCross(config.OFFSET_COLOR)
        self.cross.setVisible(False)
        self.logger = None
        self.showGrid = False
        

    def toggleGrid(self):
        self.showGrid = not self.showGrid
        
    def setLogger(self,logger):
        self.logger = logger
    
    def changed(self):
        pyglet.clock.unschedule(self.printInfo)
        pyglet.clock.schedule_once(self.printInfo,config.LOGGING_SETTLING_PERIOD)
        
    def makeGrid(self):
        pxPerDeg = self.converter.d2p(1.0)
        majorSpacing = config.RETINA_UNIT_DEG * pxPerDeg
        minorSpacing = config.RETINA_ALTERNATE_UNIT_DEG * pxPerDeg
        x0 = self.xoff
        y0 = self.yoff
        self.Mgrid = Grid(x0,y0,self.width,self.height,majorSpacing,config.TARGET_GRID_CENTER_COLOR,config.TARGET_GRID_MAJOR_COLOR,style='pluses',size=10.0)
        self.mgrid = Grid(x0,y0,self.width,self.height,minorSpacing,config.TARGET_GRID_CENTER_COLOR,config.TARGET_GRID_MINOR_COLOR,style='points',size=1.0)

    def printInfo(self,dt):
        if not self.logger is None:
            self.logger.logThis(self.info())
        else:
            print 'No logger set for RetinalLocation object.'

    def switchEye(self):
        self.eye = (self.eye+1)%2
        self.horizontalLabels.reverse()
        self.changed()
        return 'eye set to %s'%self.eyeLabels[self.eye]
    
    def moveLeft(self):
        self.xDeg = self.xDeg - self.unit
        self.changed()
        return 'retinal location: %s'%self.info()

    def moveRight(self):
        self.xDeg = self.xDeg + self.unit
        self.changed()
        return 'retinal location: %s'%self.info()

    def moveUp(self):
        self.yDeg = self.yDeg + self.unit
        self.changed()
        return 'retinal location: %s'%self.info()

    def moveDown(self):
        self.yDeg = self.yDeg - self.unit
        self.changed()
        return 'retinal location: %s'%self.info()

    def moveLeftAlt(self):
        self.xDeg = self.xDeg - self.alternateUnit
        self.changed()
        return 'retinal location: %s'%self.info()
    
    def moveRightAlt(self):
        self.xDeg = self.xDeg + self.alternateUnit
        self.changed()
        return 'retinal location: %s'%self.info()

    def moveUpAlt(self):
        self.yDeg = self.yDeg + self.alternateUnit
        self.changed()
        return 'retinal location: %s'%self.info()

    def moveDownAlt(self):
        self.yDeg = self.yDeg - self.alternateUnit
        self.changed()
        return 'retinal location: %s'%self.info()

    def setLocation(self,xDeg,yDeg):
        self.xDeg = xDeg * config.H_ORIENTATION
        self.yDeg = yDeg * config.V_ORIENTATION
        self.changed()

    def sign(self,num):
        return math.copysign(1,num)

    def info(self):
        hIdx = int(self.sign(self.xDeg*config.H_ORIENTATION)+1)
        vIdx = int(self.sign(self.yDeg*config.V_ORIENTATION)+1)
        return str('%0.2f'%abs(self.xDeg)) + self.horizontalLabels[hIdx] + \
            ', ' + str('%0.2f'%abs(self.yDeg)) + self.verticalLabels[vIdx] + \
            ' (' + self.eyeLabels[self.eye] + ')'
    def offsetInfo(self):
        return 'xoffset=%d px, yoffset=%d px'%(self.xoff-self.xoff0,self.yoff-self.yoff0)

    def xPx(self):
        return self.converter.d2p(self.xDeg)+self.xoff

    def yPx(self):
        return self.converter.d2p(self.yDeg)+self.yoff

    def increaseXOffset(self):
        self.xoff = self.xoff + config.OFFSET_UNIT_PIXELS
        self.cross.setVisible(True)
        pyglet.clock.unschedule(self.cross.setInvisible)
        pyglet.clock.schedule_once(self.cross.setInvisible,config.OFFSET_CROSS_DURATION)
        self.mgrid.xShift(config.OFFSET_UNIT_PIXELS)
        self.Mgrid.xShift(config.OFFSET_UNIT_PIXELS)
        self.changed()
        return 'retinal center offset: %s'%self.offsetInfo()

    def decreaseXOffset(self):
        self.xoff = self.xoff - config.OFFSET_UNIT_PIXELS
        self.cross.setVisible(True)
        pyglet.clock.unschedule(self.cross.setInvisible)
        pyglet.clock.schedule_once(self.cross.setInvisible,config.OFFSET_CROSS_DURATION)
        self.mgrid.xShift(-config.OFFSET_UNIT_PIXELS)
        self.Mgrid.xShift(-config.OFFSET_UNIT_PIXELS)
        self.changed()
        return 'retinal center offset: %s'%self.offsetInfo()

    def increaseYOffset(self):
        self.yoff = self.yoff + config.OFFSET_UNIT_PIXELS
        self.cross.setVisible(True)
        pyglet.clock.unschedule(self.cross.setInvisible)
        pyglet.clock.schedule_once(self.cross.setInvisible,config.OFFSET_CROSS_DURATION)
        self.mgrid.yShift(config.OFFSET_UNIT_PIXELS)
        self.Mgrid.yShift(config.OFFSET_UNIT_PIXELS)
        self.changed()
        return 'retinal center offset: %s'%self.offsetInfo()

    def decreaseYOffset(self):
        self.yoff = self.yoff - config.OFFSET_UNIT_PIXELS
        self.cross.setVisible(True)
        pyglet.clock.unschedule(self.cross.setInvisible)
        pyglet.clock.schedule_once(self.cross.setInvisible,config.OFFSET_CROSS_DURATION)
        self.mgrid.yShift(-config.OFFSET_UNIT_PIXELS)
        self.Mgrid.yShift(-config.OFFSET_UNIT_PIXELS)
        self.changed()
        return 'retinal center offset: %s'%self.offsetInfo()

    def brieflyShowOffset(self):
#         self.cross.setVisible(True)
        self.cross.toggleVisible()
        pyglet.clock.unschedule(self.cross.setInvisible)
        pyglet.clock.schedule_once(self.cross.setInvisible,config.OFFSET_CROSS_DURATION)


    def draw(self,right,top):
        label = pyglet.text.Label(self.info(),
                                  font_name=config.FONT_NAME,
                                  font_size=config.FONT_SIZE,
                                  x=right-self.textPadding, y=top-self.textPadding,
                                  anchor_x='right', anchor_y='top', color=[128,128,128,255])
        offsetLabelColor = []
        for val in config.OFFSET_COLOR:
            offsetLabelColor.append(int(round(255*val)))
        offsetLabelColor.append(255)
        offsetLabel = pyglet.text.Label(str(self.offsetInfo()),
                                        width=350,
                                        multiline=True,
                                        font_name=config.FONT_NAME,
                                        font_size=config.FONT_SIZE,
                                        x=0+self.textPadding, y=top-self.textPadding,
                                        anchor_x='left', anchor_y='top', color=offsetLabelColor)
        label.draw()

        if self.showGrid and not self.mgrid is None:
            self.mgrid.draw()

        if self.showGrid and not self.Mgrid is None:
            self.Mgrid.draw()

        self.cross.draw(self.xoff,self.yoff)
        if self.cross.visible:
            offsetLabel.draw()
        

class Console:
    '''A pseudo-console to be drawn on the target window for debugging.
    '''
    def __init__(self,right=1920,bufferLength=20,width=800):
        self.lines = []
        self.nLines = 0
        self.maxLines = bufferLength
        self.visible = False
        self.right = right
        self.top = 600
        self.targetWindowWidth = width
        self.color = [0,200,0,255]
        
    def disp(self,line):
        print line
        self.lines.append(line)
        self.nLines+=1
        if self.nLines>self.maxLines:
            self.lines = self.lines[1:]
            self.nLines-=1
    
    def toString(self):
        outstr = ''
        for line in self.lines:
            outstr = outstr + line + '\n'
        return outstr
    
    def draw(self):
        if self.visible:
            console = pyglet.text.Label(self.toString(),
                                      width=self.targetWindowWidth,
                                      multiline=True,
                                      font_name=config.CONSOLE_FONT_NAME,
                                      font_size=config.CONSOLE_FONT_SIZE,
                                      x=self.right, y=self.top,
                                      anchor_x='right', anchor_y='top', color=self.color)
            console.draw()
            
    def toggleVisible(self):
        self.visible = not self.visible

class Keys:
    '''Generates key bindings and associated help messages.
    '''
    def __init__(self,console,logger):
        self.console = console
        self.logger = logger
        self.bindings = []
        self.helpVisible = False
        self.textPadding = 10

    def add(self,symbol,modifier,func,keyinfo,funcinfo=None):
        if funcinfo==None:
            funcinfo = func.__name__
        tup = (symbol,modifier,func,keyinfo,funcinfo)
        self.bindings.append(tup)

    def section(self,sectionName):
        self.bindings.append((None,None,None,sectionName,''))
        
    def command(self,symbol,modifier):
        if not ((modifier & key.MOD_ALT) | (modifier & key.MOD_CTRL) | (modifier & key.MOD_SHIFT)):
            modifier = 0
            
        for tup in self.bindings:
            if tup[0]==symbol and ((modifier==0 and tup[1]==0) or (tup[1] & modifier)):
                self.console.disp(tup[4])
                output = tup[2]()
                if not output is None:
                    self.console.disp(output)
#                     self.logger.logThis(output)

    def helpString(self):
        helpstr = ''
        for tup in self.bindings:
            if not tup[1] is None:
                helpstr = helpstr + tup[3] + ':\t ' + tup[4] + '\n'
            else:
                helpstr = helpstr + '---------- ' + tup[3] + ' ----------\n'
        return helpstr

    def showHelp(self,dt=0.0):
        self.helpVisible = True
        
    def hideHelp(self,dt=0.0):
        self.helpVisible = False

    def toggleHelp(self):
        self.helpVisible = not self.helpVisible

    def draw(self,left,top):
        if self.helpVisible:
            label = pyglet.text.Label(self.helpString(),
                                      width=600,
                                      multiline=True,
                                      font_name=config.FONT_NAME,
                                      font_size=config.FONT_SIZE-2,
                                      x=left+self.textPadding, y=top-10*self.textPadding,
                                      anchor_x='left', anchor_y='top', color=[100,100,200,255])
            label.draw()


        
        
class Logger:
    '''Logs the position of fixation target at intervals specified by config.LOGGING_PERIOD.
    '''

    def __init__(self,loc):
        self.loc = loc
        logPath = './logs/'
        if not os.path.exists(logPath):
            os.makedirs(logPath)        
        nowStr = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        logFilename = logPath + nowStr + '_log.txt'
        self.logFid = open(logFilename,'w')

    def log(self,dt):
        nowStr = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        logLine = 'status: '+nowStr+','+self.loc.info()
        self.logFid.write(logLine+'\n')
        print logLine

    def logThis(self,text):
        nowStr = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        logLine = 'update: '+nowStr+','+text
        self.logFid.write(logLine+'\n')
        print logLine

    def close(self):
        self.logFid.close()

class Target:
    '''Superclass for target objects. Each target consists of one or more components, which can be
    added upon instantiation using the constructor's COMPONENTS parameter, or added sequentially
    using the ADD method.
    '''
    def __init__(self):
        self.components = []
        self.x = 0.0
        self.y = 0.0
        self.nStates = 10
        self.visible = True
        self.blinkers = []
        
    def add(self,component):
        self.components.append(component)

    def draw(self,x,y):
        self.x = x
        self.y = y
        self.redraw()

    def redraw(self,dt=0.0):
        for component in self.components:
            component.draw(self.x,self.y)


    def setBlink(self,applyTo=None,blinkPeriod=config.BLINK_PERIOD,dutyCycle=config.BLINK_DUTY_CYCLE):
        if applyTo is None:
            applyTo = range(len(self.components))

        self.blinkers = []

        for idx in applyTo:
            component = self.components[idx]
            component.setBlinkPeriod(blinkPeriod)
            component.setBlinkDutyCycle(dutyCycle)
            self.blinkers.append(component)
            pyglet.clock.schedule_interval(component.toggleVisible,blinkPeriod/round(1.0/(1.0-dutyCycle)))

    def increaseBlinkPeriod(self):
        newPeriod = None
        for blinker in self.blinkers:
            oldPeriod = blinker.getBlinkPeriod()
            newPeriod = oldPeriod + config.BLINK_PERIOD_ADJUSTMENT_FACTOR*oldPeriod
            dutyCycle = blinker.getBlinkDutyCycle()
            blinker.setBlinkPeriod(newPeriod)
            pyglet.clock.unschedule(blinker.toggleVisible)
            pyglet.clock.schedule_interval(blinker.toggleVisible,newPeriod/round(1.0/(1.0-dutyCycle)))
        if not newPeriod is None:
            return 'setting period to %0.1f'%newPeriod
        
    def decreaseBlinkPeriod(self):
        newPeriod = None
        for blinker in self.blinkers:
            oldPeriod = blinker.getBlinkPeriod()
            newPeriod = oldPeriod - config.BLINK_PERIOD_ADJUSTMENT_FACTOR*oldPeriod
            newPeriod = max(newPeriod,config.BLINK_PERIOD_MINIMUM)
            dutyCycle = blinker.getBlinkDutyCycle()
            blinker.setBlinkPeriod(newPeriod)
            pyglet.clock.unschedule(blinker.toggleVisible)
            pyglet.clock.schedule_interval(blinker.toggleVisible,newPeriod/round(1.0/(1.0-dutyCycle)))
        if not newPeriod is None:
            return 'setting period to %0.1f'%newPeriod

    def increaseLineWidth(self):
        for component in self.components:
            component.increaseLineWidth()

    def decreaseLineWidth(self):
        for component in self.components:
            component.decreaseLineWidth()

    def increaseRadius(self):
        for component in self.components:
            component.increaseRadius()

    def decreaseRadius(self):
        for component in self.components:
            component.decreaseRadius()

    def setColor(self,newColor):
        for component in self.components:
            component.setColor(newColor)

    def setVisible(self,newVisible):
        self.visible = newVisible
        for component in self.components:
            component.setVisible(newVisible)

    def toggleVisible(self,dt=0.0):
        self.visible = not self.visible
        for component in self.components:
            component.toggleVisible(dt)

    def setInvisible(self,dt=0.0):
        self.visible = False
        for component in self.components:
            component.setVisible(False)


class SimpleCross(Target):
    def __init__(self,color=[0.5,0.5,0.5]):
        Target.__init__(self)
        s1 = Spoke(1.0/60.0,0.5,theta=0.0,color=color)
        s2 = Spoke(1.0/60.0,0.5,theta=math.pi/2.0,color=color)
        self.add(s1)
        self.add(s2)


class BlinkyStar(Target):
    def __init__(self,LW,R):
        Target.__init__(self)
        # vertical spokes:
        x = X(LW,R,theta=0.0,color=[1.0,1.0,1.0])
        self.add(x)
        x = X(LW,R,theta=math.pi/4.0,color=[0.5,0.5,0.5])
        self.add(x)
        x = X(LW,R,theta=math.pi/4.0,color=[1.0,1.0,1.0])
        self.add(x)
        self.setBlink([2])


class Component:
    '''Superclass for target components. A component may be a line or a circle, for instance.
    A target shape, such as a star or a box, may be made up of many components.'''
    def __init__(self,lineWidthDeg,radiusDeg,theta=0.0,color=[1.0,1.0,1.0]):
        self.miniConverter = MiniConverter()
        self.d2p = self.miniConverter.d2p
        self.lineWidth = self.d2p(lineWidthDeg)
        self.radius = self.d2p(radiusDeg)
        self.color = []
        for col in color:
            self.color.append(float(col))
        self.theta = float(theta)
        self.visible = True
        self.blinkPeriod = None
        self.blinkDutyCycle = None
        
    def start(self):
        self.running = True

    def setBlinkPeriod(self,newBlinkPeriod):
        self.blinkPeriod = float(newBlinkPeriod)

    def getBlinkPeriod(self):
        return self.blinkPeriod
    
    def setBlinkDutyCycle(self,newBlinkDutyCycle):
        self.blinkDutyCycle = float(newBlinkDutyCycle)

    def getBlinkDutyCycle(self):
        return self.blinkDutyCycle

    def increaseLineWidth(self):
        self.lineWidth = self.lineWidth + self.d2p(config.LINE_WIDTH_UNIT)

    def decreaseLineWidth(self):
        self.lineWidth = max(0.0,self.lineWidth - self.d2p(config.LINE_WIDTH_UNIT))

    def increaseRadius(self):
        self.radius = self.radius + self.d2p(config.TARGET_RADIUS_UNIT)

    def decreaseRadius(self):
        self.radius = max(0.0,self.radius - self.d2p(config.TARGET_RADIUS_UNIT))

    def draw(self,x,y):
        '''Draw this component at position x,y (pixels). Assume a gl context for
        drawing is available, generated by the caller.'''
        pass

    def setColor(self,newColor):
        try:
            for idx in range(len(self.color)):
                self.color[idx] = newColor[idx]
        except Exception as msg:
            sys.exit(msg)

    def setVisible(self,newVisible):
        self.visible = newVisible

    def genSetVisible(self,newVisible):
        return (lambda: self.setVisible(newVisible))

    def toggleVisible(self,dt):
        self.visible = not self.visible
        
    def genToggleVisible(self):
        return (lambda: self.toggleVisible())

    def rotate(self,dTheta):
        self.theta = self.theta + dTheta

    def genRotate(self,dTheta):
        return (lambda: self.rotate(dTheta))



class Circle(Component):
    
    def draw(self,x,y):
        if self.visible:
            pi = math.pi
            radius = self.radius
            iterations = int(radius*2.0*pi)
            s = math.sin(2*pi / iterations)
            c = math.cos(2*pi / iterations)
            dx,dy = radius,0
            pyglet.gl.glBegin(pyglet.gl.GL_TRIANGLE_FAN)
            pyglet.gl.glColor3f(self.color[0], self.color[1], self.color[2])
            pyglet.gl.glVertex2f(x,y)
            for i in range(iterations+1):
                pyglet.gl.glVertex2f(x+dx,y+dy)
                dx,dy = (dx*c - dy*s),(dy*c + dx*s)
            pyglet.gl.glEnd()

class Spoke(Component):
    
    def draw(self,x,y):
        if self.visible:
            pi = math.pi
            cos = math.cos
            sin = math.sin
            radius = self.radius
            dTheta = math.atan(self.lineWidth/radius)

            lw2 = self.lineWidth/2.0
            thetaA = self.theta - dTheta
            thetaB = self.theta + dTheta
            x1a = radius * sin(thetaA) + x
            x2a = radius * sin(thetaA+pi) + x
            y1a = radius * cos(thetaA) + y
            y2a = radius * cos(thetaA+pi) + y
            x1b = radius * sin(thetaB) + x
            x2b = radius * sin(thetaB+pi) + x
            y1b = radius * cos(thetaB) + y
            y2b = radius * cos(thetaB+pi) + y
            pyglet.gl.glBegin(pyglet.gl.GL_QUADS)
            pyglet.gl.glColor3f(self.color[0],self.color[1],self.color[2])
            pyglet.gl.glVertex2f(x1a,y1a)
            pyglet.gl.glVertex2f(x1b,y1b)
            pyglet.gl.glVertex2f(x2a,y2a)
            pyglet.gl.glVertex2f(x2b,y2b)
            pyglet.gl.glEnd()

class X(Component):
    def draw(self,x,y):
        if self.visible:
            pyglet.gl.glBegin(pyglet.gl.GL_QUADS)

            pi = math.pi
            cos = math.cos
            sin = math.sin
            radius = self.radius
            dTheta = math.atan(self.lineWidth/radius)

            lw2 = self.lineWidth/2.0
            thetaA = self.theta - dTheta
            thetaB = self.theta + dTheta
            x1a = radius * sin(thetaA) + x
            x2a = radius * sin(thetaA+pi) + x
            y1a = radius * cos(thetaA) + y
            y2a = radius * cos(thetaA+pi) + y
            x1b = radius * sin(thetaB) + x
            x2b = radius * sin(thetaB+pi) + x
            y1b = radius * cos(thetaB) + y
            y2b = radius * cos(thetaB+pi) + y
            pyglet.gl.glColor3f(self.color[0],self.color[1],self.color[2])
            pyglet.gl.glVertex2f(x1a,y1a)
            pyglet.gl.glVertex2f(x1b,y1b)
            pyglet.gl.glVertex2f(x2a,y2a)
            pyglet.gl.glVertex2f(x2b,y2b)

            thetaA = self.theta - dTheta + pi/2.0
            thetaB = self.theta + dTheta + pi/2.0
            x1a = radius * sin(thetaA) + x
            x2a = radius * sin(thetaA+pi) + x
            y1a = radius * cos(thetaA) + y
            y2a = radius * cos(thetaA+pi) + y
            x1b = radius * sin(thetaB) + x
            x2b = radius * sin(thetaB+pi) + x
            y1b = radius * cos(thetaB) + y
            y2b = radius * cos(thetaB+pi) + y
            pyglet.gl.glVertex2f(x1a,y1a)
            pyglet.gl.glVertex2f(x1b,y1b)
            pyglet.gl.glVertex2f(x2a,y2a)
            pyglet.gl.glVertex2f(x2b,y2b)
            
            pyglet.gl.glEnd()



class Tangent(Component):
    def draw(self,x,y):
        if self.visible:
            pi = math.pi
            cos = math.cos
            sin = math.sin
            radius = self.radius
            dRadius = self.lineWidth
            theta1 = self.theta - pi/4.0
            theta2 = self.theta + pi/4.0
            radiusA = radius - dRadius
            radiusB = radius + dRadius
            x1 = radiusA * sin(theta1) + x
            x2 = radiusA * sin(theta2) + x
            y1 = radiusA * cos(theta1) + y
            y2 = radiusA * cos(theta2) + y

            x3 = radiusB * sin(theta2) + x
            x4 = radiusB * sin(theta1) + x
            y3 = radiusB * cos(theta2) + y
            y4 = radiusB * cos(theta1) + y

            pyglet.gl.glBegin(pyglet.gl.GL_QUADS)
            pyglet.gl.glColor3f(self.color[0],self.color[1],self.color[2])
            pyglet.gl.glVertex2f(x1,y1)
            pyglet.gl.glVertex2f(x2,y2)
            pyglet.gl.glVertex2f(x3,y3)
            pyglet.gl.glVertex2f(x4,y4)
            pyglet.gl.glEnd()


if __name__=='__main__':
    fta = FixationTargetApp()

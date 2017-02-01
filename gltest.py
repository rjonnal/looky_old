import pyglet
from pyglet.gl import *
import sys
import looky_config as lcfg
from pyglet.window import key

# d=dir()
# for item in d:
#     x = item.lower().find('point')
#     y = item.lower().find('size')
#     
#     if x>-1 and y>-1:
#         print eval(item)
#         
# sys.exit()

class Grid:
    '''Represents a grid of x- and y- locations. Provides methods for
    generating locations (given a center and spacing), shifting 
    locations, and drawing the grid.
    '''
    def __init__(self,x0,y0,width,height,spacing,centerColor,otherColor,style='points',size=1.0):
        self.x0 = x0
        self.y0 = y0
        self.width = width
        self.height = height
        self.xLoci = self.makeLoci(x0,width,spacing)
        self.yLoci = self.makeLoci(y0,height,spacing)
        self.cc = centerColor
        self.oc = otherColor
        self.style = style
        self.size = size
        self.spacing = spacing
        self.vertexList,self.N = self.makeVertexList(style)

    def makeLoci(self,center,length,spacing,border=lcfg.DEFAULT_GRID_BORDER):
        loci = []
        locus = center
        while locus >= -border:
            loci.append(locus)
            locus = locus - spacing
        loci.reverse()
        locus = center + spacing
        while locus < length + border:
            loci.append(locus)
            locus = locus + spacing
        return loci

    def shift1(self,dim,px):
        if dim==0:
            ulimit = self.upperXLimit
            llimit = self.lowerXLimit
        elif dim==1:
            ulimit = self.upperYLimit
            llimit = self.lowerYLimit
        else:
            sys.exit('invalid value of DIM passed to SHIFT')
        subList = self.vertexList.vertices[dim::2]
        subListMax = max(subList) - self.size/2.0
        subListMin = min(subList) + self.size/2.0
        for n in range(self.N):
            offset = self.vertexOffset[n*2+dim]
            # the offset of the point from the plus
            # center; use it to calculate whether the plus is
            # off the screen, rather than any given vertex,
            # since a vertex may move off the screen w/o needing
            # the plus to wrap around
            newVal = self.vertexList.vertices[n*2+dim]+px
            if n==0:
                print newVal,(llimit,ulimit),(subListMin,subListMax),

            if newVal-offset<llimit:
                newVal = subListMax + self.spacing + offset
                if n==0:
                    print 'cond1',
            elif newVal-offset>=ulimit:
                newVal = subListMin - self.spacing + offset
                if n==0:
                    print 'cond2',

            if n==0:
                print newVal

            self.vertexList.vertices[n*2+dim] = newVal

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
        drawType = GL_POINTS
        if self.style.lower()=='points':
            glPointSize(self.size)
            drawType = GL_POINTS
        if self.style.lower()=='pluses':
            glLineWidth(2.0)
            drawType = GL_LINES
        if self.style.lower()=='graph':
            glLineWidth(2.0)
            drawType = GL_LINES
        self.vertexList.draw(drawType)

class FixationTargetApp:
    '''This class represents the entire application. All Target
    objects are properties of this class. Also, this class owns all
    OpenGL objects, so it's responsible for making sure a context
    exists for drawing them, etc.
    '''
    def __init__(self):

        self.targetWindow = pyglet.window.Window(fullscreen=True)
        self.targetDisplay = self.targetWindow.display
        self.targetScreens = self.targetDisplay.get_screens()
        self.iTargetScreen = lcfg.TARGET_DEFAULT_SCREEN
        shiftSize = 10

        x0 = self.targetWindow.width/2.0
        y0 = self.targetWindow.height/2.0
        
        self.grid = Grid(x0,y0,self.targetWindow.width,self.targetWindow.height,173.48833,[0.5,0.5,0.5],[0.2,0.2,0.2],'graph',10)

        @self.targetWindow.event
        def on_draw():
            glClear(GL_COLOR_BUFFER_BIT)
            self.draw()

        @self.targetWindow.event
        def on_key_press(symbol,modifiers):
            if symbol == key.LEFT:
                self.grid.xShift(-shiftSize)
            if symbol == key.RIGHT:
                self.grid.xShift(shiftSize)
            if symbol == key.UP:
                self.grid.yShift(shiftSize)
            if symbol == key.DOWN:
                self.grid.yShift(-shiftSize)

        pyglet.app.run()

    
    def draw(self):
        self.grid.draw()
        

fta = FixationTargetApp()

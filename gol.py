from omega import *
from cyclops import *
from euclid import *
from ctypes import *
import copy
import math
import random


PACK_DEPTH = 31

def uint8(value):
        return c_ubyte(int(value)).value

def uint32(value):
        return c_uint(int(value)).value


class GameOfLife:
        
        MODEL = "p3GOL"
        PROGRAM = "p3GOL"
        
        STATE_ADVANCER = "Advancer"
        STATE_LIGHTBULB = "Light_Bulb"
        STATE_PUFFERTRAIN = "Puffer_Train"
        STATE_PULSARS = "Pulsars"
        STATE_VACUUMCLEANER = "Vacuum_Cleaner"
        
        def __init__(self, scene, intW, intH, floatUnit):
                self._w = intW
                self._h = intH
                self._u = floatUnit
                self._go = [[0 for y in xrange(intH)] for x in xrange(intW)]
                self._gn = copy.deepcopy(self._go)
                self._pak = [0 for x in xrange(int(math.ceil(intW * intH / float(PACK_DEPTH))))]
                self._model = None
                self._obj = None
                self._uvis = None
                
                prg = ProgramAsset()
                prg.name = GameOfLife.PROGRAM
                prg.vertexShaderName = "glsl/gol.vert"
                prg.fragmentShaderName = "glsl/gol.frag"
                scene.addProgram(prg)
                
                self._genModel()
                self._stalled = False
                
                # generate initial state sources
                self._states = {}
                self._fromImage(GameOfLife.STATE_ADVANCER, "life/advancer_80x80.png", 80, 80)
                self._fromImage(GameOfLife.STATE_LIGHTBULB, "life/light_bulb_90x50.png", 90, 50)
                self._fromImage(GameOfLife.STATE_PUFFERTRAIN, "life/puffer_train_110x80.png", 110, 80)
                self._fromImage(GameOfLife.STATE_PULSARS, "life/pulsars_120x70.png", 120, 70)
                self._fromImage(GameOfLife.STATE_VACUUMCLEANER, "life/vacuum_cleaner_110x80.png", 110, 80)
        
        def _count(self, g, x, y):
                xm = x - 1
                xp = x + 1
                ym = y - 1
                yp = y + 1
                
                if xm < 0: xm += self._w
                if xp == self._w: xp -= self._w
                if ym < 0: ym += self._h
                if yp == self._h: yp -= self._h
                   
                #count = g[ (x-1)%self._w ][ (y-1)%self._h ] + \
                #        g[ (x)%self._w   ][ (y-1)%self._h ] + \
                #        g[ (x+1)%self._w ][ (y-1)%self._h ] + \
                #        g[ (x-1)%self._w ][ (y)%self._h   ] + \
                #        g[ (x+1)%self._w ][ (y)%self._h   ] + \
                #       g[ (x-1)%self._w ][ (y+1)%self._h ] + \
                #       g[ (x)%self._w   ][ (y+1)%self._h ] + \
                #        g[ (x+1)%self._w ][ (y+1)%self._h ]
                count = g[ xm ][ ym ] + \
                        g[ xm ][ y  ] + \
                        g[ xm ][ yp ] + \
                        g[ x   ][ ym ] + \
                        g[ x   ][ yp ] + \
                        g[ xp ][ ym ] + \
                        g[ xp ][ y   ] + \
                        g[ xp ][ yp ]
                        
                return count

        
        def _swap(self):
                tmp = self._go
                self._go = self._gn
                self._gn = tmp
        
        
        def _pack(self):
                for i in xrange(len(self._pak)): self._pak[i] = 0
                
                for x in xrange(self._w):
                        for y in xrange(self._h):
                                if self._gn[x][y] == 0: continue
                        
                                idx = x * self._h + y
                                shift = idx % PACK_DEPTH
                                idx = idx // PACK_DEPTH
                                mask = 1 << shift
                                #print "x: %d y: %d  idx: %d   len: %d" % (x, y, idx, len(self._pak))
                                self._pak[idx] = self._pak[idx] | mask
        
     
        def Apply(self, start, stop):
                if self._stalled: return
        
                o = self._go
                n = self._gn
                
                for x in xrange(start, stop):
                        for y in xrange(self._h): 
                                count = self._count(o, x, y)
                                
                                old = o[x][y]
                                
                                if old == 0:
                                        if count == 3: n[x][y] = 1
                                        else: n[x][y] = 0
                                else:
                                        if count < 2 or count > 3: n[x][y] = 0
                                        else: n[x][y] = 1

                
                
        
        def ApplyUpperHalf(self):
                self.Apply(0, self._w / 2)
                
        def ApplyBottomHalf(self):
                self.Apply(self._w / 2, self._w)
                self._pack()               
                self._swap()
        
        def Test(self):
                n = self._gn
                
                n[0][0] = 0
                n[0][1] = 0
                n[1][0] = 1
                n[1][1] = 1
                
                print(n)
                
                self._pack()
                print(self._pak)
       
        
        def Update(self):
                if self._uvis == None: return
                for i in xrange(len(self._pak)):
                        #print "i: %d  val: %d  bin: %s" % (i, self._pak[i], bin(self._pak[i]))
                        self._uvis.setIntElement(self._pak[i], i)
                #print("")
                 
       
        def Random(self):
                random.seed()
                for x in xrange(self._w):
                        for y in xrange(self._h):
                                self._go[x][y] = math.floor(random.random() * 2)
                                
        def FromState(self, state):
                tp = self._states[state]
                self._genFromPixels(tp[0], tp[1], tp[2])
                                
                          
        def _clear(self, grid):
                for x in xrange(self._w):
                        for y in xrange(self._h):
                                grid[x][y] = 0
                                
                                
        def _genFromPixels(self, pd, gx, gy):
                self._clear(self._gn)
                self._clear(self._go)
                
                maxX = pd.getWidth()
                maxY = pd.getHeight()
                
                cell = maxY / gy
                shift = cell / 2
                
                pd.beginPixelAccess()
                for x in xrange(gx):
                        px = x * cell + shift
                        for y in xrange(gy):
                                py = y * cell + shift
                                red = pd.getPixelR(px, py)
                                green = pd.getPixelG(px, py)
                                blue = pd.getPixelB(px, py)
                                if (red > 128 and green < 128 and blue < 128):
                                        self._go[x][y] = 1
                                else:
                                        self._go[x][y] = 0
                pd.endPixelAccess()
                
        
        def _fromImage(self, strName, strPath, gx, gy):
                pd = loadImage(strPath)
                self._states[strName] = pd, gx, gy
       
        
        @staticmethod
        def _encodeID(intID):
                c2 = intID // 255
                c1 = intID % 255
                return Color(1.0, 0.0, c2, c1)
 
                
        def _genModel(self):
                geom = ModelGeometry.create(GameOfLife.MODEL)
                t = self._u
                
                vcount = 0
                pcount = 0
                for w in xrange(self._w):
                        for h in xrange(self._h):             
                                m = Matrix4()
                                m.translate(w*t, 0, h*t)
                                
                                v0 = m.transform(Vector3(0, 0, 0))
                                v1 = m.transform(Vector3(0, t, 0))
                                v2 = m.transform(Vector3(t, 0, 0))
                                v3 = m.transform(Vector3(t, t, 0))
                                v4 = m.transform(Vector3(t, 0, t))
                                v5 = m.transform(Vector3(t, t, t))
                                v6 = m.transform(Vector3(0, 0, t))
                                v7 = m.transform(Vector3(0, t, t))
                                
                                # this will tell us what to discard in vs
                                color = GameOfLife._encodeID(pcount)
                                
                                geom.addVertex(v0)
                                geom.addColor(color)
                                geom.addVertex(v1)
                                geom.addColor(color)
                                geom.addVertex(v2)
                                geom.addColor(color)
                                geom.addVertex(v3)
                                geom.addColor(color)
                                geom.addVertex(v4)
                                geom.addColor(color)
                                geom.addVertex(v5)
                                geom.addColor(color)
                                geom.addVertex(v6)
                                geom.addColor(color)
                                geom.addVertex(v7)
                                geom.addColor(color)
                                geom.addVertex(v0)
                                geom.addColor(color)
                                geom.addVertex(v1)
                                geom.addColor(color)
                                
                                geom.addVertex(v5)
                                geom.addColor(color)
                                geom.addVertex(v3)
                                geom.addColor(color)
                                geom.addVertex(v7)
                                geom.addColor(color)
                                geom.addVertex(v1)
                                geom.addColor(color)
                                
                                geom.addPrimitive(PrimitiveType.TriangleStrip, vcount, 14)
                                vcount += 14
                                pcount += 1

                self._model = geom
              

        def AddToScene(self, scene):
                scene.addModel(self._model)
                
                
                self._obj = StaticObject.create(GameOfLife.MODEL)
                self._obj.setEffect(GameOfLife.MODEL)
                self._uvis = Uniform.create('u_Visibility', UniformType.Int, len(self._pak))
                self._obj.getMaterial().attachUniform(self._uvis)
                
                self._obj.setPosition(-5, 0, 0)
                self._obj.setSelectable(False)
        
        
        def SceneNode(self):
                return self._obj
        
        
        def _Stall(self, event):
                ray = getRayFromEvent(event)
                
                if not ray[0]: return                
                
                hit = hitNode(self._obj, ray[1], ray[2])                            
                if hit[0]:
                        self.Stall()


        def _Unstall(self, event):
                ray = getRayFromEvent(event)
                
                if not ray[0]: return                
                
                hit = hitNode(self._obj, ray[1], ray[2])                            
                if hit[0]:
                        self.Unstall()            

                
        def Stall(self):
                self._stalled = True
                
        def Unstall(self):            
                self._stalled = False
                print("Unstalled")

       
        def Intersect(self, event):
                
                ray = getRayFromEvent(event)
                
                if not ray[0]: return
                
                hit = hitNode(self._obj, ray[1], ray[2])                            
                if hit[0]:
                        pt = self._obj.convertWorldToLocalPosition(hit[1])            
                        #print(pt)
                        
                        cx = min(int(pt.x / self._u), self._w-1) 
                        cy = min(int(pt.z / self._u), self._h-1) 
                                       
                        print(cx, cy)
                        self._go[cx][cy] = 1
                        self._gn[cx][cy] = 1
                        self._pack()
                        #self._swap()      
                                
                                
                                
                                
                                
                                
                                
                                
                                

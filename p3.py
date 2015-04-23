from math import *
from euclid import *
from omega import *
from cyclops import *
from omegaToolkit import *
from walkabout import walkabout
from gol import *

import profile

scene = getSceneManager()
ui = UiModule.createAndInitialize()
wf = ui.getWidgetFactory()
uiroot = ui.getUi()

root = SceneNode.create('everything')

scene.setShaderMacroToString('unlit', "");

walkabout.init(getDefaultCamera())
walkabout.setFloorCheck(True)
walkabout.setWallCheck(True)


camctl = getDefaultCamera().getController()
camctl.setSpeed(camctl.getSpeed() * 4)

# Unicontroller
class UC:

        ACTION_P = 0
        ACTION_H = 1
        ACTION_R = 2
        
        _cbs = {\
                ACTION_P: set(),\
                ACTION_H: set(),\
                ACTION_R: set()\
                }
        
        _held = set()

        _cachedEvent = None
                
        @staticmethod
        def ActionPress(event):
                UC._notify(UC.ACTION_P, event)
                UC._held.add(UC.ACTION_H)
        
        @staticmethod       
        def ActionRelease(event):
                UC._notify(UC.ACTION_R, event)
                UC._held.discard(UC.ACTION_H)    
                
        @staticmethod
        def _notify(key, event):
                for cb in UC._cbs[key]:
                        cb(event)
        
        @staticmethod             
        def Subscribe(key, cb):
                UC._cbs[key].add(cb)

        @staticmethod             
        def Unsubscribe(key, cb):
                UC._cbs[key].discard(cb)
        
        @staticmethod
        def Cache(event):
                UC._cachedEvent = event
        
        @staticmethod       
        def UpdateHeld():
                for key in UC._held:
                        UC._notify(key, UC._cachedEvent)


scene.createProgramFromString("glow", 
# Vertex shader
'''
	varying vec2 var_TexCoord;
	varying vec3 var_Normal;
	varying vec3 var_EyeVector;

	void main(void)
	{
		gl_Position = ftransform();
		vec4 eyeSpacePosition = gl_ModelViewMatrix * gl_Vertex;
		
		var_TexCoord = gl_MultiTexCoord0.xy;
		
		var_EyeVector = -eyeSpacePosition.xyz;
		var_Normal = gl_NormalMatrix * gl_Normal;
		
		gl_FrontColor = gl_Color;
	}
''',
'''
//#define ITER 50
//#define COLOR vec3(1.0, 0.65, 0.1)

uniform vec2 variant;
//varying vec2 surfacePosition;
varying vec2 var_TexCoord;

vec2 cmul(in vec2 a, in vec2 b)
{
    float r, i;
    r = a.x*b.x - a.y*b.y;
    i = a.x*b.y + a.y*b.x;
    return vec2(r, i);
}

void main( void ) {
	vec3 COLOR = vec3(1.0, 0.65, 0.1);
	int ITER = 50;
	vec2 c = variant * 2.0 - 1.0;
	vec2 z = var_TexCoord * 2.0 - vec2(1.0, 0.0);
	float iter = 0.0;
	
	for (int i = 0; i < ITER; i++)
	{
		z = cmul(z, z) + c;
		if (length(z) > 2.0)
		{
			iter = float(i) / float(ITER);
			break;
		}
	}
	
	gl_FragColor = vec4(iter*COLOR*2.0, 1.0);
}
''')


# Fragment shader
'''
	varying vec2 var_TexCoord;
	uniform float unif_Glow;

	void main (void)
	{
		float vx = pow(abs((var_TexCoord.x - 0.5) * 2.0), unif_Glow);
		float vy = pow(abs((var_TexCoord.y - 0.5) * 2.0), unif_Glow);

		gl_FragColor.rgb = gl_Color.rgb;	
		gl_FragColor.a = (vx + vy);
	}
'''#)

# effect programs
prg = ProgramAsset()
prg.name = "Wave"
prg.vertexShaderName = "glsl/effect.vert"
prg.fragmentShaderName = "glsl/wave.frag"
scene.addProgram(prg)

prg = ProgramAsset()
prg.name = "WaveStripes"
prg.vertexShaderName = "glsl/effect.vert"
prg.fragmentShaderName = "glsl/wavestripes.frag"
scene.addProgram(prg)

prg = ProgramAsset()
prg.name = "Flare"
prg.vertexShaderName = "glsl/effect.vert"
prg.fragmentShaderName = "glsl/flare.frag"
scene.addProgram(prg)


class GpuArtMgr:

        _lsttp = list()
        
        @staticmethod
        def New(strEffect, boolTime, boolInput, v2Size, v3Pos, yaw):
                
                if v2Size is None: v2Size = Vector2(2, 1)
                ent = PlaneShape.create(v2Size.x, v2Size.y)
                
                if v3Pos is None: v3Pos = Vector3(0, 0, 0)
                ent.setPosition(v3Pos)
                
                if yaw: ent.yaw(yaw)
                
                ent.setEffect(strEffect)
                
                u_time = None
                if boolTime:
                        u_time = ent.getMaterial().addUniform('u_time', UniformType.Float)
                        u_time.setFloat(0.0)
                        
                u_input = None
                if boolInput:
                        u_input = ent.getMaterial().addUniform('u_input', UniformType.Vector2f)
                        u_input.setVector2f(Vector2(0.5, 0.5))
                
                invSize = 1.0 / (v2Size * 0.5)
                        
                tpArt = ent, u_time, u_input, invSize
                GpuArtMgr._lsttp.append(tpArt)
                
                return ent
                
        @staticmethod
        def TimeUpdate(time):
                for tp in GpuArtMgr._lsttp:
                        if tp[1]:
                                tp[1].setFloat(time)
                                
        @staticmethod
        def _inputUpdate(event):
                ray = getRayFromEvent(event)
                if not ray[0]: return

                for tp in GpuArtMgr._lsttp:
                        if tp[2] is None: continue
                        hit = hitNode(tp[0], ray[1], ray[2])
                        if hit[0]:
                                pt = tp[0].convertWorldToLocalPosition(hit[1])            
                                norm = Vector2(pt.x * tp[3].x, pt.y * tp[3].y)
                                tp[2].setVector2f(norm)
                        
        @staticmethod
        def Init():
                UC.Subscribe(UC.ACTION_H, GpuArtMgr._inputUpdate)

GpuArtMgr.Init()

# artwork
srWaveStripes = GpuArtMgr.New("WaveStripes", True, True, Vector2(25.5, 18), Vector3(-39.5, 9, -5), radians(90))
srFlares = GpuArtMgr.New("Flare", True, True, Vector2(23, 18), Vector3(-28, 9, 8), radians(180))
srWaves = GpuArtMgr.New("Wave", True, True, Vector2(23, 18), Vector3(-28, 9, -17.9), radians(0))




prg = ProgramAsset()
prg.name = "ColoredUnlit"
prg.vertexShaderName = "glsl/colored_unlit.vert"
prg.fragmentShaderName = "glsl/colored_unlit.frag"
scene.addProgram(prg)
scene.setShaderMacroToFile("vertexShader", "glsl/default.vert")
scene.setShaderMacroToFile("surfaceShader", "glsl/default.frag")








##boxg = BoxShape.create(0.8, 0.8, 0.8)
##boxg.setPosition(Vector3(0, 2, -3))
##boxg.setEffect("glow -d green -t")

##boxg.setEffect("glow -d red -t")
#lowPower = boxg.getMaterial().addUniform('unif_Glow', UniformType.Float)
#glowPower.setFloat(10)
plane = PlaneShape.create(2, 1)
plane.setPosition(0, 2, -2)
plane.setEffect("glow")
variant = plane.getMaterial().addUniform('variant', UniformType.Vector2f)
variant.setVector2f(Vector2(0, 0))

boxr = BoxShape.create(0.8, 0.8, 0.8)
boxr.setPosition(Vector3(-2, 2, -6))
boxr.setEffect("colored -d red")

boxb = BoxShape.create(0.8, 0.8, 0.8)
boxb.setPosition(Vector3(2, 2, -6))
#boxb.setEffect("LineGLow")
boxb.getMaterial().setProgram("ColoredUnlit")
boxb.getMaterial().setColor(Color(0.0, 0.0, 1.0, 1.0), Color(0.0, 0.0, 1.0, 1.0))
print(boxb.getMaterialCount())
boxb.getMaterial().setWireframe(True)
#boxb.getMaterial().setDoubleFace(True)










def createGridModel(strName, w, l, d):
	model = ModelGeometry.create(strName)
	
	lhw = 0.01
	
	count = 0
	
	vCount = int(math.floor(w / d))
	for i in range(vCount+1):
		
		x1 = i * d - lhw
		x2 = i * d + lhw
		y1 = lhw
		y2 = -l - lhw
		
	
		sw = Vector3(x1, 0, y1)
		nw = Vector3(x1, 0, y2)
		se = Vector3(x2, 0, y1)
		ne = Vector3(x2, 0, y2)
		
		print(ne)
		
		model.addVertex(sw)
		model.addVertex(se)
		model.addVertex(nw)
		model.addVertex(ne)
		
		model.addPrimitive(PrimitiveType.TriangleStrip, count, 4)
		count += 4
		
	hCount = int(math.floor(l / d))
	for i in range(hCount+1):
		
		x1 = -lhw
		x2 = w + lhw
		y1 = i * -d + lhw
		y2 = y1 - 2 * lhw
		
	
		sw = Vector3(x1, 0, y1)
		nw = Vector3(x1, 0, y2)
		se = Vector3(x2, 0, y1)
		ne = Vector3(x2, 0, y2)
		
		print(ne)
		
		model.addVertex(sw)
		model.addVertex(se)
		model.addVertex(nw)
		model.addVertex(ne)
		
		model.addPrimitive(PrimitiveType.TriangleStrip, count, 4)
		count += 4
		
	return model
		
		
gridModel = createGridModel("grid1", 100, 50, 1)
scene.addModel(gridModel)

grid = StaticObject.create("grid1")
grid.setEffect("colored -d blue")
gridFl = PlaneShape.create(100, 54)
gridFl.setEffect("colored -d black")
gridFl.pitch(radians(-90))
gridFl.setPosition(46.0, -0.005, -25.0)
grid.addChild(gridFl)
grid.setPosition(-40, 0.01, 6)
root.addChild(grid)
grid.setSelectable(True)










# tree model
treeModel = ModelInfo()
treeModel.name = "tree"
treeModel.path = "models/tree.fbx"
scene.loadModel(treeModel)
treeModel.generateNormals = True
treeModel.optimize = True

# Create a scene object using the loaded model
tree = StaticObject.create("tree")
tree.setEffect("colored -d blue")
tree.setPosition(-27, 0, -5)
tree.setScale(1.0, 2.0, 1.0)

# tree model
treetModel = ModelInfo()
treetModel.name = "tree_tall"
treetModel.path = "models/tree_tall.fbx"
scene.loadModel(treetModel)
treetModel.generateNormals = True
treetModel.optimize = True

# Create a scene object using the loaded model
tree_tall1 = StaticObject.create("tree_tall")
tree_tall1.setPosition(-36, 0, 3.5)

tree_tall2 = StaticObject.create("tree_tall")
tree_tall2.setPosition(-36, 0, -15)
tree_tall2.yaw(radians(64))



# room model
roomModel = ModelInfo()
roomModel.name = "room"
roomModel.path = "models/room.fbx"
scene.loadModel(roomModel)
roomModel.generateNormals = False
roomModel.optimize = True

# Create a scene object using the loaded model
room = StaticObject.create("room")
room.getMaterial().setProgram("ColoredUnlit")
room.getMaterial().setColor(Color(0.0, 0.0, 1.0, 1.0), Color(0.0, 0.0, 1.0, 1.0))
room.getMaterial().setWireframe(True)
room.getMaterial().setDoubleFace(True)
room.setPosition(Vector3(0, 0, -6))
room.setSelectable(True)


# room model
shadesModel = ModelInfo()
shadesModel.name = "shades"
shadesModel.path = "models/shades.fbx"
scene.loadModel(shadesModel)
shadesModel.generateNormals = False
shadesModel.optimize = True

# Create a scene object using the loaded model
shades = StaticObject.create("shades")
shades.setEffect("colored -d black")
shades.getMaterial().setColor(Color(0.0, 0.0, 0.0, 1.0), Color(0.0, 0.0, 0.0, 1.0))
shades.setPosition(Vector3(0, 0, -6))


# arrows model
arrowsModel = ModelInfo()
arrowsModel.name = "arrows"
arrowsModel.path = "models/arrows.fbx"
scene.loadModel(arrowsModel)
arrowsModel.generateNormals = False
arrowsModel.optimize = True

# Create a scene object using the loaded model
arrows = StaticObject.create("arrows")
arrows.setEffect("colored -d blue")
arrows.setPosition(Vector3(2, 4, -18))



gol = GameOfLife(scene, 120, 80, 0.2)
gol.AddToScene(scene)
gol.Random()
gol.SceneNode().setPosition(Vector3(26.0, 4.0, -8.5))
gol.SceneNode().pitch(radians(-90))

# GOL UI
class GolMgr:

        _btns = {}
        
        @staticmethod 
        def NewBtn(strName, pos, cb):
                c = wf.createContainer("container" + str(strName), uiroot, ContainerLayout.LayoutFree)
                c.setAutosize(False)
                c.setSize(Vector2(800, 100))
                c.setStyle('fill: black; border: 20 white;')
                l = wf.createLabel('label', c, strName)
                l.setSize(c.getSize())
                l.setAutosize(False)
                l.setStyle('font: fonts/arial.ttf 80; color: white')
                c.setPixelOutputEnabled(True)
                texTXT = "texture" + strName
                scene.createTexture(texTXT, c.getPixels())

                b = BoxShape.create(2.0, 0.2, 0.01)
                b.setPosition(pos)
                b.setEffect("textured -d " + texTXT)
                b.setSelectable(True)
                b.setName("button" + strName)
                b.setFacingCamera(getDefaultCamera())
                
                GolMgr._btns[strName] = b, c, l, cb
                return b
                
        @staticmethod
        def _update(event):
                ray = getRayFromEvent(event)
                if not ray[0]: return
                
                it = GolMgr._btns.itervalues()
                for tp in it:
                        hit = hitNode(tp[0], ray[1], ray[2])
                        if hit[0]:
                                if tp[3]: tp[3]()
                                
        @staticmethod
        def Init():
                UC.Subscribe(UC.ACTION_P, GolMgr._update)

GolMgr.Init()          

golBtnStall = GolMgr.NewBtn("Stall", Vector3(42.5, 12, -38), lambda: gol.Stall())                
golBtnStart = GolMgr.NewBtn("Start", Vector3(42.5, 11.8, -38), lambda: gol.Unstall())
golBtnState1 = GolMgr.NewBtn(GameOfLife.STATE_ADVANCER, Vector3(36, 12, -38),\
        lambda: gol.FromState(GameOfLife.STATE_ADVANCER))
golBtnState2 = GolMgr.NewBtn(GameOfLife.STATE_LIGHTBULB, Vector3(36, 11.8, -38),\
        lambda: gol.FromState(GameOfLife.STATE_LIGHTBULB))
golBtnState3 = GolMgr.NewBtn(GameOfLife.STATE_PUFFERTRAIN, Vector3(36, 11.6, -38),\
        lambda: gol.FromState(GameOfLife.STATE_PUFFERTRAIN))
golBtnState4 = GolMgr.NewBtn(GameOfLife.STATE_PULSARS, Vector3(36, 11.4, -38),\
        lambda: gol.FromState(GameOfLife.STATE_PULSARS))
golBtnState5 = GolMgr.NewBtn(GameOfLife.STATE_VACUUMCLEANER, Vector3(36, 11.2, -38),\
        lambda: gol.FromState(GameOfLife.STATE_VACUUMCLEANER))
golBtnState6 = GolMgr.NewBtn("Random", Vector3(36, 11, -38),\
        lambda: gol.Random())


# Place a light
light = Light.create()
light.setColor(Color("white"))
light.setAmbient(Color("#202020"))
light.setEnabled(True)

light2 = Light.create()
light2.setColor(Color("white"))
light2.setAmbient(Color("#202020"))
light2.setEnabled(True)
light2.setPosition(40, 13, -40)





cl = scene.getCompositingLayer()#CompositingLayer()
cl.loadCompositor("uglify.xml")





def doIt():
        gol.Apply()
        gol.Update()
        
#profile.run('doIt()')
UC.Subscribe(UC.ACTION_P, gol._Stall)
UC.Subscribe(UC.ACTION_H, gol.Intersect)
UC.Subscribe(UC.ACTION_R, gol._Unstall)




tGolUp = 0.0
golSecond = False
def onUpdate(frame, t, dt):
    global tGolUp
    global golSecond
    
    # artwork updates
    GpuArtMgr.TimeUpdate(t)
    
    # controller "input held" updates
    UC.UpdateHeld()
    
    walkabout.update(dt)
    
    #boxg.pitch(dt)
    #boxg.yaw(dt / 3)
    boxr.pitch(dt)
    boxr.yaw(dt / 3)
    boxb.pitch(dt)
    boxb.yaw(dt / 3)
    
    cPos = getDefaultCamera().getPosition()
    vPos = Vector2(math.fmod(math.fabs(cPos.x), 1), math.fmod(math.fabs(cPos.y), 1))
    #print(vPos)
    variant.setVector2f(vPos)
    
    
    if not golSecond:
        gol.ApplyUpperHalf()
        golSecond = True
    else:
        gol.ApplyBottomHalf()
        gol.Update()
        golSecond = False
    #tGolUp += dt
    #if tGolUp > 0.06:
    #        gol.Apply()
    #        #gol.Test()
    #        gol.Update()
    #        tGolUp = 0.0


setUpdateFunction(onUpdate)


def onEvent():
	e = getEvent()
	
	UC.Cache(e)
	
	if e.getServiceType() == ServiceType.Pointer:
	        
	        if e.isButtonDown(EventFlags.Button2):
		        print("Mouse button down")
			UC.ActionPress(e)
			
	        if e.isButtonUp(EventFlags.Button2):
	                UC.ActionRelease(e)
			
	elif e.getServiceType() == ServiceType.Wand:

		if e.isButtonDown(EventFlags.Button5):
		        print("Wand button down")
			UC.ActionPress(e)
			
		if e.isButtonUp(EventFlags.Button5):
	                UC.ActionRelease(e)


setEventFunction(onEvent)   
    

#getDefaultCamera().setPosition(Vector3(38.00, 15.32, 30.59))
#getDefaultCamera().setPosition(Vector3(1.0, 0.0, -1.0))
getDefaultCamera().setPosition(Vector3(38.66, 10.07, -39))

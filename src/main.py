# import necessary modules
import pygame
from scene import Scene
from lightSource import LightSource
from blender import load_obj_file
from BaseModel import DrawModelFromMesh
from shaders import *
from ShadowMapping import *
from skyBox import *
from environmentMapping import *

class JungleScene(Scene):
    def __init__(self):
        Scene.__init__(self)

        # initialise the light source with position and lighting values
        self.light = LightSource(self, position=[-5, 10, 5], Ia=[0.2,0.2,0.2], Id=[0.9,0.9,0.9], Is=[1,1,1])

        # for shadow map rendering
        self.shadows = ShadowMap(light=self.light)
        self.show_shadow_map = ShowTexture(self, self.shadows)

        # values to standardise object placement
        terrainScale = 0.065
        verticalTranslation = -7

        # load each of the .obj files
        water = load_obj_file('models/jungleModels/water.obj')
        self.water = DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0, -5.6, 0]), scaleMatrix([55,1,55])), mesh=water[0], shader=Shader('phong'))

        terrain = load_obj_file('models/jungleModels/terrain.obj')
        self.terrain = [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,verticalTranslation,0]), scaleMatrix([terrainScale,terrainScale,terrainScale])), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows)) for mesh in terrain]
        
        trees = load_obj_file('models/jungleModels/trees.obj')
        self.trees = [DrawModelFromMesh(scene=self, M=np.matmul(np.matmul(translationMatrix([0,verticalTranslation,0]), scaleMatrix([terrainScale,terrainScale,terrainScale])),rotationMatrixZ(-np.pi/2)), mesh=mesh, shader=Shader('phong')) for mesh in trees]
        
        shadow_models = load_obj_file('models/jungleModels/shadows.obj')
        self.shadow_models = [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,verticalTranslation,0]), scaleMatrix([terrainScale,terrainScale,terrainScale])), mesh=mesh, shader=Shader('phong')) for mesh in shadow_models]
        
        shrubs = load_obj_file('models/jungleModels/shrubs.obj')
        self.shrubs = [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,verticalTranslation,0]), scaleMatrix([terrainScale,terrainScale,terrainScale])), mesh=mesh, shader=Shader('phong')) for mesh in shrubs]

        # draw a skybox
        self.skybox = SkyBox(scene=self)

    def draw_shadow_map(self):

        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for model in self.shadow_models:
            model.draw()
        for model in self.trees:
            model.draw()
        
    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene
        :return: None
        '''

        # enable face culling for efficiency
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # render the shadows
        self.shadows.render(self)

        # when rendering the framebuffer we ignore the reflective object
        if not framebuffer:
            self.show_shadow_map.draw()
        

        # draw all of the models
        # disable face culling only when drawing the trees. without this the trees look bad
        glDisable(GL_CULL_FACE)
        for model in self.trees:
            model.draw()
        glEnable(GL_CULL_FACE)

        for model in self.terrain:
            model.draw()

        for model in self.shadow_models:
            model.draw()

        for model in self.shrubs:
            model.draw()

        # set the water alpha so that it is transparent
        self.water.mesh.material.alpha = 0.23

        # enable GL_BLEND to draw transparent models
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 
        self.water.draw()
        glDisable(GL_BLEND)

        # draw the skybox
        self.skybox.draw()

        # display the scene
        # use double buffering to avoid artefacts
        # draw on a different buffer than displayed buffer,
        # and flip the two buffers after drawing
        if not framebuffer:
            pygame.display.flip()

if __name__ == '__main__':
    
    print("Running JungleScene, please wait...")

    # initialises the scene object
    scene = JungleScene()

    # starts drawing the scene
    scene.run()

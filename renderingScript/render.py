import bpy
import os, sys
import numpy
from math import pi
from bpy import context
from mathutils import Vector

#Set the folder where the STL files are located
localSTLFolder = "/home/thefroggy/Documents/MVA/ObjectRecognition/project/Data/LegoPiecesSTL/"

#Set the folder where the images are going to be rendered
# !!! Absolute path mandatory !!! #
# !!! Must be an empty folder !!! #
renderingFolder = "/home/thefroggy/Documents/MVA/ObjectRecognition/project/Data/LegoPiecesBlender/"

#Number of point of views
nPov = 100

#Computing the radius
def computeBoxRad(obj,center):
  bestRad = 0.
  for b in obj.bound_box:
    bVec=Vector([b[0],b[1],b[2]])
    curRad = (bVec-center).length
    bestRad = curRad if curRad > bestRad else bestRad 
  return bestRad

def remove_obj_lamp_and_mesh(context):
    scene = context.scene
    objs = bpy.data.objects
    meshes = bpy.data.meshes
    for obj in objs:
        if obj.type == 'MESH' or obj.type == 'LAMP':
            scene.objects.unlink(obj)
            objs.remove(obj)
    for mesh in meshes:
        meshes.remove(mesh)

def getRandomPointAroundSphere(center,radius):
   theta = numpy.random.uniform(0.,1.)*pi
   phi = numpy.random.uniform(0.,2.)*pi
   x = radius * numpy.sin( theta ) * numpy.cos( phi )
   y = radius * numpy.sin( theta ) * numpy.sin( phi )
   z = radius * numpy.cos( theta )
   return (x+center[0],y+center[1],z+center[2])

def getMaterial(red,green,blue):
  mat = bpy.data.materials.get("Material")
  if mat is None:
    # create material
    mat = bpy.data.materials.new(name="Material")
  mat.diffuse_color = [red, green, blue]
  return mat

#Find the files in the folder
for file in os.listdir(localSTLFolder):
  if file.endswith(".STL"):
    os.makedirs(renderingFolder+file[0:-4])
    remove_obj_lamp_and_mesh(bpy.context)
    print('Processing file '+file)
    #Import the mesh in current file in blender
    bpy.ops.import_mesh.stl(filepath=localSTLFolder, filter_glob="*.STL",  files=[{"name":localSTLFolder+file}], directory=".")
    #Get the current object
    obj = context.active_object
    #Get the coordinates of the center of mass
    local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
    global_bbox_center = obj.matrix_world * local_bbox_center
    rad = computeBoxRad(obj,global_bbox_center)
    #Creating a lamp
    # Create new lamp datablock
    lamp_data = bpy.data.lamps.new(name="Lamp", type='POINT')
    lamp_data.distance = rad * 2.5 
    lamp_data.energy = rad/28.6
    # Create new object with our lamp datablock
    lamp_object = bpy.data.objects.new(name="Lamp", object_data=lamp_data)
    # Link lamp object to the scene so it'll appear in this scene
    scene = bpy.context.scene
    scene.objects.link(lamp_object)
    rad = 5 * rad
    # Assign material to object
    mat = getMaterial(255,0,0)
    if obj.data.materials:
    # assign to 1st material slot
      obj.data.materials[0] = mat
    else:
    # no slots
      obj.data.materials.append(mat)
    for i in range(nPov): #For every point on view
      xCam,yCam,zCam = getRandomPointAroundSphere(global_bbox_center,rad)
      if(len(bpy.data.cameras) == 1):
        objCam = bpy.data.objects['Camera'] # bpy.types.Camera
        #Place the camera
        objCam.location.x = xCam
        objCam.location.y = yCam
        objCam.location.z = zCam
        bpy.data.cameras[bpy.context.scene.camera.name].clip_end = 1E6
        #Point the camera to the object
        direction = local_bbox_center - Vector([xCam,yCam,zCam])
        # point the cameras '-Z' and use its 'Y' as up
        dirUp = 'X' if numpy.random.randint(2) == 0 else 'Y'
        rot_quat = direction.to_track_quat('-Z', dirUp)
        # assume we're using euler rotation
        scene.camera.rotation_mode = 'XYZ'
        objCam.rotation_euler = rot_quat.to_euler()
        lamp_object.location = (xCam, yCam, zCam+10)
        #lamp_object.data = lamp_data
        #Render the scene 
        bpy.data.scenes['Scene'].render.filepath = renderingFolder+file[0:-4]+'/'+file[0:-4]+'_'+str(i)+'.jpg'

        # redirect output to log file
        logfile = 'blender_render.log'
        open(logfile,'a').close()
        old = os.dup(1)
        sys.stdout.flush()
        os.close(1)
        os.open(logfile, os.O_WRONLY)

        bpy.ops.render.render(write_still=True) 

        # disable output redirection
        os.close(1)
        os.dup(old)
        os.close(old)



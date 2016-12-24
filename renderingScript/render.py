import bpy
import os, sys
import numpy
import csv
from math import pi
from bpy import context
from mathutils import Vector, Matrix 

### BEGINNING OF THE USER PARAMETERS ###

#Set the folder where the STL files are located
localSTLFolder = "/home/thefroggy/Documents/MVA/ObjectRecognition/project/Data/LegoPiecesSTL/"

#Set the folder where the images are going to be rendered
# !!! Absolute path mandatory !!! #
# !!! Must be an empty folder !!! #
renderingFolder = "/home/thefroggy/Documents/MVA/ObjectRecognition/project/Data/LegoPiecesBlender/"

#Set the assembly rules folder

assemblyFolder = "/home/thefroggy/Documents/MVA/ObjectRecognition/project/Data/assemblyRules/"

#Number of point of views
nPov = 100

### END OF THE USER PARAMETERS ###

#Parsing the assembly files
def parseAssemblies(path):
  assemblies = dict()
  for file in os.listdir(path): #For each assembly file
    if file.endswith(".csv"):
      with open(path+file, 'rt') as f:
        reader = csv.reader(f,delimiter=';')
        assembly = []
        for row in reader: #For each file in the current assembly
          if row[0] == "PieceName":
            continue
          curPiece = dict()
          curPiece["Name"] = row[0]
          curPiece["RGB"] = (int(row[1]),int(row[2]),int(row[3]))
          curPiece["Matrix"] = Matrix(((float(row[4]),float(row[5]),float(row[6]),float(row[7])),(float(row[8]),float(row[9]),float(row[10]),float(row[11])),(float(row[12]),float(row[13]),float(row[14]),float(row[15])),(float(row[16]),float(row[17]),float(row[18]),float(row[19]))))
          assembly.append(curPiece)
        assemblies[file[0:-4]] = assembly
  return assemblies

#Computing the radius
def computeBoxRad(obj,center):
  bestRad = 0.
  for b in obj.bound_box:
    bVec=Vector([b[0],b[1],b[2]])
    curRad = (bVec-center).length
    bestRad = curRad if curRad > bestRad else bestRad 
  return bestRad

#Function to clean the blender workspace
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

#Get a random point on the surface of the sphere (center,radius)
def getRandomPointAroundSphere(center,radius):
   theta = numpy.random.uniform(0.,1.)*pi
   phi = numpy.random.uniform(0.,2.)*pi
   x = radius * numpy.sin( theta ) * numpy.cos( phi )
   y = radius * numpy.sin( theta ) * numpy.sin( phi )
   z = radius * numpy.cos( theta )
   return (x+center[0],y+center[1],z+center[2])

#Make a material with the specified name, and the specified color
def getMaterial(fileName,red,green,blue):
  mat = bpy.data.materials.new(name="Material"+fileName)
  mat.diffuse_color = [red, green, blue]
  return mat

#Creating a lamp with an appropriate energy
def makeLamp(rad):
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
  return lamp_object

#Render the current frame with a redirection of the flow in a log file
def renderWithoutOutput():
  # redirect output to log file
  logfile = 'blender_render.log'
  open(logfile,'a').close()
  old = os.dup(1)
  sys.stdout.flush()
  os.close(1)
  os.open(logfile, os.O_WRONLY)
  #Render
  bpy.ops.render.render(write_still=True) 
  # disable output redirection
  os.close(1)
  os.dup(old)
  os.close(old)


#Rendering procedure for the assemblies
assemblies = parseAssemblies(assemblyFolder)
print('Found ' + str(len(assemblies)) + ' assemblies to be rendered')
for key,assembly in assemblies.items(): #For each assembly
  remove_obj_lamp_and_mesh(bpy.context) #Cleaning the blender workspace
  os.makedirs(renderingFolder+key) #Making an appropriate directory
  print('Processing assembly '+key)
  for fileInfo in assembly: #For each file in the assembly
    file = fileInfo["Name"]
    #Import the mesh in current file in blender
    bpy.ops.import_mesh.stl(filepath=localSTLFolder, filter_glob="*.STL",  files=[{"name":localSTLFolder+file}], directory=".")
    #Get the current object
    obj = context.active_object
    #Move object to its place
    obj.matrix_world = fileInfo["Matrix"]
    # Assign material to object
    mat = getMaterial(file,*fileInfo["RGB"])
    if obj.data.materials:
    # assign to 1st material slot
      obj.data.materials[0] = mat
    else:
    # no slots
      obj.data.materials.append(mat)
  obj = context.active_object
  #Get the coordinates of the center of mass and the radius
  local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
  global_bbox_center = obj.matrix_world * local_bbox_center
  rad = computeBoxRad(obj,global_bbox_center)
  #Add a lamp (its intensity depends on rad)
  lamp_object = makeLamp(rad)
  rad = 5 * rad #We will place the camera away from the object
  for i in range(nPov): #For every point on view
    xCam,yCam,zCam = getRandomPointAroundSphere(global_bbox_center,rad)
    if(len(bpy.data.cameras) == 1):
      objCam = bpy.data.objects['Camera']
      #Place the camera
      objCam.location = (xCam,yCam,zCam)
      bpy.data.cameras[bpy.context.scene.camera.name].clip_end = 1E6
      #Point the camera to the object
      direction = local_bbox_center - Vector([xCam,yCam,zCam])
      # point the cameras '-Z' and use its 'Y' as up
      dirUp = 'X' if numpy.random.randint(2) == 0 else 'Y'
      rot_quat = direction.to_track_quat('-Z', dirUp)
      # assume we're using euler rotation
      context.scene.camera.rotation_mode = 'XYZ'
      objCam.rotation_euler = rot_quat.to_euler()
      #Place the lamp
      lamp_object.location = (xCam, yCam, zCam+10)
      #Render the scene 
      bpy.data.scenes['Scene'].render.filepath = renderingFolder+key+'/'+key+'_'+str(i)+'.png'
      renderWithoutOutput()



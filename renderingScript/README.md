# Rendering tool for STL files

* Download blender : sudo apt-get install blender
* Download python 3 : sudo apt-get install python3
* Set the parameters at the beginning of the file render.py
* Create the assembly files (see next section) and put it in the assembly rules folder that you have specified in render.py
* run launch\_renderer.sh
 
# The assembly files

The assembly files are csv file that explain blender how to build a renderable assembly from the raw STL files. As a consequence, you must create as much assembly file as classes that you want to render. An example assembly file is given in assembly1.csv

The structure of this file is pretty simple. The first line gives the description of the fields used for each column. Each line after the first one represents one part that is added to the assembly.

Here are the required features for each part : 

* The name of the STL file so that the algorithm can find it. (Just the name is sufficient. The path is known from the parameters that you must have set in render.py)
* The diffuse color of the part (RGB)
* Its world matrix which represents its position in space. In order to have it, we recommand to place the assembly in blender. Once the assembly is perfectly fitted, do the following procedure for each part in the assembly : select the part with right click ; open the python3 console in blender and type `bpy.context.active_object.matrix_world`.



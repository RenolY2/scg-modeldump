# scg-modeldump
Tool that dumps the .nod model files of Starcraft Ghost into .obj format.

# Download
Download this tool by clicking on the green Code button and click Download Zip.

# How to use
You need to install a recent version of Python 3 (e.g. 3.8 or newer). When installing, make sure you click on "Add Python to PATH" at the start of the installer. 

Copy the files convertall.py, parse.py, read_nod.py and vectors.py into the root directory of Starcraft Ghost (in the same place where e.g. Ghost.exe is). Run convertall.py by double-clicking convertall.py or you can open the command prompt in the same folder as convertall.py (using Shift+Right click) and then type in ``python convertall.py``. This will convert all .nod files in the \3D\Models\ folder to .obj files which are written into a \converted_models\ folder that the tool creates. You can import the obj files using e.g. Blender to view the models.

# Notes
This tool does not preserve character rigs and skeletons (and the .obj file format does not support rigging anyway). If you want to pose characters you will have to create your own skeleton and do your own rigging, or you research how .nod handles skeletons and rigging and then expand this tool (or create your own tool) which converts .nod into a format capable of rigging, e.g. dae (collada)

Some models look like they have missing textures. In some cases the tool failed to find the correct texture, you might be able to fix this manually in a 3d modelling program of your choice by finding the correct texture (.dds file) for the material. In other cases there's really no texture for the model or model part because the model is unfinished.

Some models, e.g. nova.nod, look messed up. It is unknown how that could be fixed.

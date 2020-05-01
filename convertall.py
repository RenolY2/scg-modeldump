import subprocess 
import os 
from parse import read_material_file
from read_nod import NodModel

folder = ".\\3D\\Models"
"""
for file in os.listdir(folder):
    fullpath = os.path.join(folder, file)
    if fullpath.endswith(".nod"):
        with open(fullpath, "rb") as f:
            try:
                with open(fullpath+".obj", "w") as g:
                    nod = NodModel.from_file(f, g)
            except:
                print(fullpath, "failed")"""
                

def find_all_textures(folderpath):
    textures = {}
    for path, dirs, files in os.walk(folderpath):
        for file in files:
            if file.endswith(".dds"):
                textures[file] = os.path.join(path, file)
    
    return textures

from shutil import copyfile

mat2texture = {}
textures = find_all_textures(".")
print("found all textures")
matpath = "./Materials/"

for tex in textures:
    path = textures[tex]
    basename = os.path.basename(path)
    copyfile(path, os.path.join("./converted_models/textures", basename))
    textures[tex] = os.path.join("./textures", basename)


lowercases = {}
for texture in textures:
    lowercases[texture.lower()] = texture

for file in os.listdir(matpath):
    if file.endswith(".nsa"):
        with open(os.path.join(matpath, file), "r") as f:
            materials = read_material_file(f)
        for mat, data in materials.items():
            if "texture" in data:
                tex = data["texture"]
                if tex in textures: 
                    mat2texture[mat.lower()] = textures[tex]
                elif tex+".dds" in textures:
                    mat2texture[mat.lower()] = textures[tex+".dds"]
                elif tex.lower() in lowercases:
                    mat2texture[mat.lower()] = textures[lowercases[tex.lower()]]
                elif tex.lower()+".dds" in lowercases:
                    mat2texture[mat.lower()] = textures[lowercases[tex.lower()+".dds"]]

"""for mat in mat2texture:
    path = mat2texture[mat]
    basename = os.path.basename(path)
    copyfile(path, os.path.join("./converted_models/textures", basename))
    mat2texture[mat] = os.path.join("./textures", basename)"""

#import json 
#with open("materials.json", "w") as f:
#    json.dump(mat2texture, f, indent=4)
for file in os.listdir(folder):
    #if True:
    #folder = "D:/StarCraftGhost/StarCraft Ghost Xbox Finn Hillbilly/3D/Models"
    #file = "goliath_blue.nod"
    fullpath = os.path.join(folder, file)
    if fullpath.endswith(".nod"):
        basename = os.path.basename(fullpath)
        
        with open(fullpath, "rb") as f:
            objpath = os.path.join("./converted_models/", basename)
            with open(objpath+".obj", "w") as g:
                with open(objpath+".mtl", "w") as h:
                    try:
                        model = NodModel.from_file(f, g, h, basename+".mtl", mat2texture, textures)
                    except Exception as err:
                        print(fullpath, "failed because", err)
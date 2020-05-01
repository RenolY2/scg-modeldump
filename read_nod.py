import struct 
from vectors import Vector3, Vector2
from parse import read_material_file
import os 

def read_uint8(f):
    return struct.unpack("B", f.read(1))[0]

def read_uint16(f):
    return struct.unpack("H", f.read(2))[0]

def read_uint32(f):
    return struct.unpack("I", f.read(4))[0]
    
def read_float(f):
    return struct.unpack("f", f.read(4))[0]


class Boundary(object):
    def __init__(self, start, end):
        self.start = start 
        self.end = end 
    
    @classmethod
    def from_file(cls, f):
        start = Vector3(read_float(f), read_float(f), read_float(f))
        end = Vector3(read_float(f), read_float(f), read_float(f))
        return cls(start, end)


class LevelOfDetail(object):
    def __init__(self, stripCount, listCount, vtxCount, indexOffset):
        self.stripStart = indexOffset
        self.stripCount = stripCount 
        self.listStart = indexOffset+stripCount 
        self.listCount = listCount 
        self.vtxCount = vtxCount 
    
    @classmethod
    def from_file(cls, f, indexOffset):
        return cls(read_uint16(f), read_uint16(f), read_uint16(f), indexOffset)
        

class Bone(object):
    def __init__(self):
        pass 
    
    @classmethod
    def from_file(cls, f):
        start = f.tell()
        restTranslate = Vector3(read_float(f), read_float(f), read_float(f))
        f.seek(start+0x30)
        invTranslate = Vector3(read_float(f), read_float(f), read_float(f))
        val = read_uint32(f)
        parentID = (val >> 0x10) & 0xFF
        tagID = (val >> 0x18) & 0xFF
        f.seek(start+0x40)
        
        
class MeshGroupFile(object):
    def __init__(self):
        pass 
    
    @classmethod
    def from_file(cls, f, indexOffset):
        start = f.tell()
        meshGroupFile = cls()
        meshGroupFile.materialid = read_uint32(f)
        meshGroupFile.lods = []
        
        for i in range(4):
            lod = LevelOfDetail.from_file(f, indexOffset)
            meshGroupFile.lods.append(lod)
            indexOffset += lod.stripCount + lod.listCount
            
        meshGroupFile.vertexCount = read_uint16(f)
        meshGroupFile.groupFlags = read_uint8(f)
        meshGroupFile.blendShapeCount = read_uint8(f)
        meshGroupFile.blendGroup = read_uint8(f)
        meshGroupFile.bones = f.read(20)
        meshGroupFile.boneCount = read_uint8(f)
        meshGroupFile.vtxGroup = read_uint8(f)
        f.read(1) # padd
        print(hex(f.tell() - start))
        assert f.tell() - start == 0x38 
        return meshGroupFile, indexOffset


class Vertex(object):
    def __init__(self, pos, normal=None, uv=None):
        self.pos = pos 
        self.normal = normal 
        self.uv = uv


class NodModel(object):
    def __init__(self):
        pass
        
    @classmethod
    def from_file(cls, f, out, outmat, mtlname, materials, textures):
        version = read_uint32(f)
        assert version == 0xA 
        shaderCount = read_uint8(f)
        boneCount = read_uint8(f)
        vertGroupCount = read_uint8(f)
        meshGroupCount = read_uint8(f)
        flags = read_uint32(f)
        boundary = Boundary.from_file(f)
        
        vtxgroups = []
        for i in range(4):
            vtxtype = read_uint8(f)
            f.read(3) # padd 
            vtxcount = read_uint32(f)
            
            vtxgroups.append((vtxtype, vtxcount))
        indexCount = read_uint32(f)
        lodStarts = [read_uint32(f) for i in range(4)]
        assert f.tell() == 88
        lodCount = read_uint8(f)
        f.seek(0x5C)
        shaders = []
        for i in range(shaderCount):
            name = f.read(0x20).strip(b"\x00")
            shaders.append(name.decode("ascii"))
        
        bones = []
        for i in range(boneCount):
            bone = Bone.from_file(f)
            bones.append(bone)
            
        if boneCount == 0:
            bone = Bone()
            bones.append(bone)
        
        vertexGroups = []
        
        #with open("model.obj", "w") as g:
        if True:
            for shader in shaders:
                print(shader.lower(), shader.lower() in materials)
                if shader.lower() in materials:
                    texpath = materials[shader.lower()]
                else:
                    if shader in textures:
                        texpath = textures[shader]
                    elif shader+".dds" in textures:
                        texpath = textures[shader+".dds"]
                    else:
                        texpath="NotFound"
                outmat.write("newmtl {0}\n".format(shader))
                outmat.write("map_kd {0}\n".format(texpath))
                
            out.write("mtllib {0}\n".format(mtlname))
            g = out
            print("vert group count", vertGroupCount)
            for i in range(vertGroupCount):
                group = []
                verttype, vertcount = vtxgroups[i]
                
                print(verttype, vertcount)
                #assert verttype == 0
                if verttype == 0 or verttype == 3:
                    for i in range(vertcount):
                        start = f.tell()
                        vertexpos = Vector3(read_float(f), read_float(f), read_float(f))
                        normal = Vector3(read_float(f), read_float(f), read_float(f))
                        uv = Vector3(read_float(f), read_float(f), 0.0)
                        assert f.tell() - start == 0x20
                        #g.write("v {0} {1} {2}\n".format(vertexpos.x, vertexpos.z, -vertexpos.y))
                        group.append(Vertex(vertexpos, uv=uv))
                elif verttype == 1:
                     for i in range(vertcount):
                        start = f.tell()
                        vertexpos = Vector3(read_float(f), read_float(f), read_float(f))
                        normal = Vector3(read_float(f), read_float(f), read_float(f))
                        uv = Vector3(read_float(f), read_float(f), 0.0)
                        f.read(4)
                        assert f.tell() - start == 0x24
                        #g.write("v {0} {1} {2}\n".format(vertexpos.x, vertexpos.z, -vertexpos.y))
                        group.append(Vertex(vertexpos, uv=uv))
                elif verttype == 2:
                     for i in range(vertcount):
                        start = f.tell()
                        vertexpos = Vector3(read_float(f), read_float(f), read_float(f))
                        normal = Vector3(read_float(f), read_float(f), read_float(f))
                        uv = Vector3(read_float(f), read_float(f), 0.0)
                        f.read(0x30-0x20)
                        assert f.tell() - start == 0x30
                        #g.write("v {0} {1} {2}\n".format(vertexpos.x, vertexpos.z, -vertexpos.y))
                        group.append(Vertex(vertexpos, uv=uv))
                
                else:
                    raise RuntimeError("Unknown vtx type {0}".format(verttype))
                    pass
                vertexGroups.append(group)
            
            indices = []
            for i in range(indexCount):
                indices.append(read_uint16(f))
            
            meshes = []
            index = 0
            for i in range(meshGroupCount):
                mesh, index = MeshGroupFile.from_file(f, index)
                meshes.append(mesh)
            
            vtxGroupOffsets = []
            for i in range(vertGroupCount):
                if i == 0:
                    vtxGroupOffsets.append(0)
                else:
                    vtxGroupOffsets.append(len(vertexGroups[i-1]))
            
            for group in vertexGroups:
                for vertex in group:
                    vertexpos = vertex.pos
                    uv = vertex.uv
                    g.write("v {0} {1} {2}\n".format(vertexpos.x, vertexpos.z, -vertexpos.y))
                    if uv is not None:
                        g.write("vt {0} {1}\n".format(uv.x, 1.0-uv.y))
            
            #meshes.pop(0)
            #meshes.pop(0)
            vtxOffset = 0
            k = 0
            drawMesh = 4
            
            out.write("o {0}\n".format(os.path.basename(mtlname)[:-4]))
            for mesh in meshes:
                
                #print(mesh.materialid)
                out.write("usemtl {0}\n".format(shaders[mesh.materialid]))
                mainlod = mesh.lods[0]
                print(mesh.vtxGroup, vtxGroupOffsets)
                print("Mesh has", mainlod.stripCount, "strips")
                """if k != drawMesh:
                    vtxOffset += mesh.vertexCount
                    k += 1
                    continue"""
                if mainlod.stripCount > 0:
                    v1, v2, v3 = None, None, None 
                    
                    n = 0
                    
                    for i in range(mainlod.stripStart, mainlod.stripStart+mainlod.stripCount):
                        if v1 is None:
                            v1 = indices[i]
                            continue 
                        elif v2 is None:
                            v2 = indices[i]
                            continue 
                        elif v3 is None:
                            v3 = indices[i]
                        else:
                            v1 = v2 
                            v2 = v3 
                            v3 = indices[i]
                        
                        offset = vtxGroupOffsets[mesh.vtxGroup]
                        #offset = 0
                        if n == 0:
                            g.write("f {0}/{0} {1}/{1} {2}/{2}\n".format(v1+1+vtxOffset, v2+1+vtxOffset, v3+1+vtxOffset))
                        else:
                            g.write("f {0}/{0} {1}/{1} {2}/{2}\n".format(v1+1+vtxOffset, v3+1+vtxOffset, v2+1+vtxOffset,))
                        n = (n+1)%2
                
                print("Mesh has", mainlod.listCount, "lists")
                if mainlod.listCount > 0:
                    for i in range(mainlod.listCount//3):
                        v1 = indices[mainlod.listStart + i*3]
                        v2 = indices[mainlod.listStart + i*3+1]
                        v3 = indices[mainlod.listStart + i*3+2]
                        offset = vtxGroupOffsets[mesh.vtxGroup]
                        #offset = 0
                        g.write("f {0}/{0} {1}/{1} {2}/{2}\n".format(v1+1+vtxOffset, v2+1+vtxOffset, v3+1+vtxOffset))
                vtxOffset += mesh.vertexCount
                #if k == 4:
                #    break 
                k += 1
if __name__ == "__main__":
    #with open("BorgoWelcomeSign.nod", "rb") as f:
    import sys 
    with open("3dMaterials.nsa", "r") as f:
        materials = read_material_file(f)
        
    input = sys.argv[1]
    output = input+".obj"
    with open(input, "rb") as f:
        with open(output, "w") as g:
            with open(input+".mtl", "w") as h:
                model = NodModel.from_file(f, g, h, input+".mtl", materials)
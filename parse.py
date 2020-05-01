def read_next_notcomment(f):
    line = f.readline()
    if not line:
        return None 
    else:
        line = line.strip()
        if not line or line.startswith(";") or line.startswith("//"):
            return read_next_notcomment(f)
        else:
            return line 
    

def read_material(f):
    name = read_next_notcomment(f) 
    print(name)
    if name is None:
        return None, None 
        
    openBracket = read_next_notcomment(f)
    assert openBracket == "{"
    line = read_next_notcomment(f)
    params = {}
    indent_level = 0
    while line != "}" or (line == "}" and indent_level > 0):
        if line == "{":
            indent_level += 1 
        elif line == "}":
            indent_level -= 1
        else:
            data = line.split(maxsplit=1)
            if len(data) > 0:
                if len(data) == 1:
                    param = data[0]
                    val = None 
                else:
                    param, val = data
                params[param] = val 
        line = read_next_notcomment(f)
        if line is None:
            break 

    return name, params 

def read_material_file(f):
    materials = {}
    mat = read_material(f)
    while mat[0] is not None:
        name, data = mat 
        materials[name] = data
        mat = read_material(f)
    return materials 
    
if __name__ == "__main__":  
    import json 
    
    with open("3dMaterials.nsa", "r") as f:
        with open("3dmaterials.json", "w") as g:
            json.dump(read_material_file(f), g, indent=4)
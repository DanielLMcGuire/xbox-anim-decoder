def write_obj(path, verts, faces, header=""):
    with open(path, 'w') as f:
        if header:
            f.write(header + "\n")
        for v in verts:
            f.write(f"v {v[0]:.5f} {v[1]:.5f} {v[2]:.5f}\n")
        for (a, b, c) in faces:
            f.write(f"f {a+1} {b+1} {c+1}\n")


def indices_to_tris(indices):
    return [tuple(indices[i:i+3]) for i in range(0, len(indices)-2, 3)]


def _write_uv_block(f, verts, faces, voffset=0):
    for (x, y, z, u, v) in verts:
        f.write(f"v {x:.5f} {y:.5f} {z:.5f}\n")
    for (x, y, z, u, v) in verts:
        f.write(f"vt {u:.5f} {1.0-v:.5f}\n")
    for (a, b, c) in faces:
        f.write(f"f {voffset+a+1}/{voffset+a+1} {voffset+b+1}/{voffset+b+1} {voffset+c+1}/{voffset+c+1}\n")


def write_obj_with_uv(path, verts, faces):
    with open(path, 'w') as f:
        _write_uv_block(f, verts, faces)


def write_obj_with_uv_grouped(path, mesh_groups):
    with open(path, 'w') as f:
        voffset = 0
        for name, verts, faces in mesh_groups:
            f.write(f"o {name}\n")
            _write_uv_block(f, verts, faces, voffset)
            voffset += len(verts)

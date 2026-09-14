import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from obj_writer import indices_to_tris, write_obj_with_uv, write_obj_with_uv_grouped

meshes = json.load(open('./meshes_decoded.json'))

os.makedirs('./obj', exist_ok=True)
total_v = 0
total_t = 0
mesh_groups = []
for name, m in meshes.items():
    verts = m['verts']
    faces = indices_to_tris(m['indices'])
    write_obj_with_uv(f"obj/{name}.obj", verts, faces)
    total_v += len(verts)
    total_t += len(faces)
    mesh_groups.append((name, verts, faces))
    print(f"{name}: {len(verts)} verts, {len(faces)} tris -> obj/{name}.obj")

print("TOTAL", total_v, "verts", total_t, "tris")

write_obj_with_uv_grouped('obj/xbox_logo_combined.obj', mesh_groups)
print("combined written")

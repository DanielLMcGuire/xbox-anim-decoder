import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from geom_core import load_quats, get_world_mat
from scene_builder import primitive_types, build_instances
from obj_writer import write_obj

data = json.load(open('./parsed_data.json'))
quats = load_quats()


def static_world_mat(matScale, matOffset, idxPosAnim, idxRotAnim):
    return get_world_mat(matScale, matOffset, idxPosAnim, idxRotAnim)


all_verts, all_faces = [], []
for ptype in primitive_types(data):
    verts, faces = build_instances(ptype, data, quats, static_world_mat)
    base = len(all_verts)
    all_verts.extend(verts)
    all_faces.extend((base+a, base+b, base+c) for (a, b, c) in faces)
    print(f"after {ptype['name']}:", len(all_verts), "verts", len(all_faces), "faces")

write_obj('./scene_primitives.obj', all_verts, all_faces)
print("DONE. total verts:", len(all_verts), "total faces:", len(all_faces))

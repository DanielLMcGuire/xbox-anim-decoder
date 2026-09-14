import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'primitives'))
from geom_core import load_quats, get_world_mat
from scene_builder import primitive_types, build_instances
from obj_writer import write_obj
from decode_anim_full import compute_anim_state

FPOS = 0.5

data = json.load(open('../primitives/parsed_data.json'))
quats = load_quats()
surfofrev_vers = json.load(open('./surfofrev_vers.json'))
pos_anims, rot_anims = compute_anim_state(FPOS, quats)


def mid_frame_world_mat(matScale, matOffset, idxPosAnim, idxRotAnim):
    return get_world_mat(matScale, matOffset, idxPosAnim, idxRotAnim, pos_anims, rot_anims)


outdir = './obj_mid'
os.makedirs(outdir, exist_ok=True)

combined_verts, combined_faces = [], []
for ptype in primitive_types(data, surfofrev_vers):
    verts, faces = build_instances(ptype, data, quats, mid_frame_world_mat)
    write_obj(f'{outdir}/{ptype["name"]}.obj', verts, faces, f"# {ptype['label']} fpos={FPOS}")

    base = len(combined_verts)
    combined_verts.extend(verts)
    combined_faces.extend((base+a, base+b, base+c) for (a, b, c) in faces)
    print(f"{ptype['name']}:", len(verts), len(faces))

write_obj(f'{outdir}/all_primitives_combined.obj', combined_verts, combined_faces,
          f"# All primitives combined for fpos={FPOS}")
print("TOTAL combined:", len(combined_verts), len(combined_faces))

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'primitives'))
from geom_core import mat_scale, make_offset_mat, transform_point
from geom_gen import (create_sphere_version, create_box_version, create_cylinder_version,
                       create_cone_version, create_torus_version, create_surf_of_rev_version)

def _cached(cache, key, build_fn):
    if key not in cache:
        cache[key] = build_fn()
    return cache[key]


def _sphere_type(data):
    cache = {}

    def local_geom(inst):
        idVersion = int(inst[3])
        return _cached(cache, idVersion, lambda: create_sphere_version(
            int(data['theSphereVers'][idVersion][0]), ndet_bias=0))

    return dict(name='spheres', label='Spheres', inst_key='theSphereInsts', local_geom=local_geom,
                scale_mat=lambda inst: mat_scale(inst[6], inst[6], inst[6]),
                quat_idx=lambda inst: None, translation=lambda inst: inst[0:3],
                pos_anim_idx=lambda inst: inst[4], rot_anim_idx=lambda inst: inst[5])


def _box_type(data):
    cache = {}

    def local_geom(inst):
        return _cached(cache, 0, create_box_version)

    return dict(name='boxes', label='Boxes', inst_key='theBoxInsts', local_geom=local_geom,
                scale_mat=lambda inst: mat_scale(inst[9], inst[7], inst[8]),
                quat_idx=lambda inst: int(inst[0]), translation=lambda inst: inst[1:4],
                pos_anim_idx=lambda inst: inst[5], rot_anim_idx=lambda inst: inst[6])


def _cylinder_type(data):
    cache = {}

    def local_geom(inst):
        idVersion = int(inst[4])

        def build():
            nHeightSeg_full, nSides_full = data['theCylinderVers'][idVersion]
            return create_cylinder_version(int(nSides_full), int(nHeightSeg_full), ndet_bias=0)
        return _cached(cache, idVersion, build)

    return dict(name='cylinders', label='Cylinders', inst_key='theCylinderInsts', local_geom=local_geom,
                scale_mat=lambda inst: mat_scale(inst[7], inst[7], inst[8]*2.0),
                quat_idx=lambda inst: int(inst[0]), translation=lambda inst: inst[1:4],
                pos_anim_idx=lambda inst: inst[5], rot_anim_idx=lambda inst: inst[6])


def _torus_type(data):
    cache = {}

    def local_geom(inst):
        idVersion = int(inst[4])

        def build():
            fRatio, nSegs_full, nSides_full = data['theTorusVers'][idVersion]
            return create_torus_version(fRatio, int(nSegs_full), int(nSides_full), ndet_bias=0)
        return _cached(cache, idVersion, build)

    return dict(name='tori', label='Tori', inst_key='theTorusInsts', local_geom=local_geom,
                scale_mat=lambda inst: mat_scale(inst[7], inst[7], inst[7]),
                quat_idx=lambda inst: int(inst[0]), translation=lambda inst: inst[1:4],
                pos_anim_idx=lambda inst: inst[5], rot_anim_idx=lambda inst: inst[6])


def _cone_type(data):
    cache = {}

    def local_geom(inst):
        idVersion = int(inst[4])

        def build():
            fRad1, fRad2, fHeight, nHeightSeg_full, nSides_full = data['theConeVers'][idVersion]
            return create_cone_version(fRad1, fRad2, fHeight, int(nHeightSeg_full), int(nSides_full), ndet_bias=0)
        return _cached(cache, idVersion, build)

    return dict(name='cones', label='Cones', inst_key='theConeInsts', local_geom=local_geom,
                scale_mat=lambda inst: mat_scale(1.0, 1.0, 1.0),
                quat_idx=lambda inst: int(inst[0]), translation=lambda inst: inst[1:4],
                pos_anim_idx=lambda inst: inst[5], rot_anim_idx=lambda inst: inst[6])


def _surf_of_rev_type(data, surfofrev_vers):
    cache = {}

    def local_geom(inst):
        idVersion = int(inst[4])

        def build():
            v = surfofrev_vers[idVersion]
            return create_surf_of_rev_version(v['pts'], (v['ax'], v['ay'], v['az']),
                                               (v['px'], v['py'], v['pz']), v['nSegs'], ndet_bias=0)
        return _cached(cache, idVersion, build)

    return dict(name='surfaces_of_revolution', label='Surfaces of revolution',
                inst_key='theSurfOfRevInsts', local_geom=local_geom,
                scale_mat=lambda inst: mat_scale(1.0, 1.0, 1.0),
                quat_idx=lambda inst: int(inst[0]), translation=lambda inst: inst[1:4],
                pos_anim_idx=lambda inst: inst[5], rot_anim_idx=lambda inst: inst[6])


def primitive_types(data, surfofrev_vers=None):
    types = [_sphere_type(data), _box_type(data), _cylinder_type(data),
             _torus_type(data), _cone_type(data)]
    if surfofrev_vers is not None:
        types.append(_surf_of_rev_type(data, surfofrev_vers))
    return types


def build_instances(ptype, data, quats, world_mat_for):
    verts, faces = [], []
    for inst in data[ptype['inst_key']]:
        local_pos, local_tris = ptype['local_geom'](inst)
        matScale = ptype['scale_mat'](inst)
        matOffset = make_offset_mat(quats, ptype['quat_idx'](inst), *ptype['translation'](inst))
        world_mat = world_mat_for(matScale, matOffset, ptype['pos_anim_idx'](inst), ptype['rot_anim_idx'](inst))

        base = len(verts)
        for p in local_pos:
            verts.append(transform_point(p, world_mat))
        for (a, b, c) in local_tris:
            faces.append((base + a, base + b, base + c))
    return verts, faces

import math
import numpy as np
from geom_core import sincos, rot_from_rh_quat, quat_from_axis_angle, transform_vector

def strip_to_tris(indices):
    tris = []
    for i in range(len(indices)-2):
        a,b,c = indices[i], indices[i+1], indices[i+2]
        if a==b or b==c or a==c:
            continue
        if i % 2 == 0:
            tris.append((a,b,c))
        else:
            tris.append((b,a,c))
    return tris

def fan_to_tris(indices):
    tris = []
    hub = indices[0]
    for i in range(1, len(indices)-1):
        tris.append((hub, indices[i], indices[i+1]))
    return tris

def create_sphere_version(nSegs_full, ndet_bias=0):
    nSegs = nSegs_full >> ndet_bias
    nSlices = nSegs // 2
    fDeltaTheta = (2*math.pi)/nSegs
    fDeltaPhi = math.pi/(nSlices-1)

    positions = []
    for i in range(nSlices):
        fPhi = fDeltaPhi*i
        sinPhi, cosPhi = sincos(fPhi)
        for j in range(nSegs):
            fTheta = fDeltaTheta*j
            sinTheta, cosTheta = sincos(fTheta)
            positions.append((cosPhi, cosTheta*sinPhi, sinTheta*sinPhi))

    indices = []
    wCurVert = 0
    for i in range(nSlices-1):
        wStartVert = wCurVert
        for j in range(nSegs+1):
            indices.append(wCurVert+nSegs)
            indices.append(wCurVert)
            if j < nSegs-1:
                wCurVert += 1
            else:
                wCurVert = wStartVert
        wCurVert += nSegs
    tris = strip_to_tris(indices)
    return positions, tris

def create_box_version():
    faces = [
        [(0.5,-0.5,0.5),(0.5,0.5,0.5),(0.5,0.5,-0.5),(0.5,-0.5,-0.5)],
        [(0.5,0.5,0.5),(-0.5,0.5,0.5),(-0.5,0.5,-0.5),(0.5,0.5,-0.5)],
        [(-0.5,0.5,0.5),(-0.5,-0.5,0.5),(-0.5,-0.5,-0.5),(-0.5,0.5,-0.5)],
        [(-0.5,-0.5,0.5),(0.5,-0.5,0.5),(0.5,-0.5,-0.5),(-0.5,-0.5,-0.5)],
        [(-0.5,0.5,0.5),(0.5,0.5,0.5),(0.5,-0.5,0.5),(-0.5,-0.5,0.5)],
        [(-0.5,-0.5,-0.5),(0.5,-0.5,-0.5),(0.5,0.5,-0.5),(-0.5,0.5,-0.5)],
    ]
    positions = []
    tris = []
    for i, quad in enumerate(faces):
        positions.extend(quad)
        base = i*4
        tris.append((base, base+1, base+2))
        tris.append((base, base+2, base+3))
    return positions, tris

def _side_wall_strip(nsides, nHeightSeg, start_index):
    cols = nsides+1
    indices = []
    wCurVert = start_index
    for row in range(nHeightSeg):
        wStartVert = wCurVert
        for j in range(cols+1) if False else range(nsides+1):
            indices.append(wCurVert+cols)
            indices.append(wCurVert)
            if j < nsides-1:
                wCurVert += 1
            else:
                wCurVert = wStartVert
        wCurVert += cols
    return indices

def create_cylinder_version(nSides_full, nHeightSeg, ndet_bias=0):
    nsides = nSides_full >> ndet_bias
    fDeltaZ = 1.0/nHeightSeg
    fDeltaTheta = (2*math.pi)/nsides

    ppts = []
    for i in range(nsides+1):
        fTheta = fDeltaTheta*i
        sinT, cosT = sincos(fTheta)
        ppts.append((cosT, sinT, fTheta/(2*math.pi)))

    positions = []
    for i in range(nsides-1, -1, -1):
        positions.append((ppts[i][0], ppts[i][1], 1.0))
    for i in range(nsides):
        positions.append((ppts[i][0], ppts[i][1], 0.0))
    for i in range(nHeightSeg+1):
        fZ = fDeltaZ*i
        for j in range(nsides+1):
            positions.append((ppts[j][0], ppts[j][1], fZ))

    indices = []
    wStartCap = 0
    top_fan = list(range(0, nsides))
    wStartCap += nsides
    bot_fan = list(range(nsides, 2*nsides))
    wStartCap += nsides

    tris = []
    tris.extend(fan_to_tris(top_fan))
    tris.extend(fan_to_tris(bot_fan))
    side_strip = _side_wall_strip(nsides, nHeightSeg, wStartCap)
    tris.extend(strip_to_tris(side_strip))
    return positions, tris

def create_cone_version(fRad1, fRad2, fHeight, nHeightSeg, nSides_full, ndet_bias=0):
    nsides = nSides_full >> ndet_bias
    fDeltaTheta = (2*math.pi)/nsides

    ppts_bot = []
    ppts_top = []
    for i in range(nsides+1):
        fTheta = fDeltaTheta*i
        sinT, cosT = sincos(fTheta)
        ppts_bot.append((cosT*fRad1, sinT*fRad1, fTheta/(2*math.pi)))
        ppts_top.append((cosT*fRad2, sinT*fRad2, fTheta/(2*math.pi)))

    fDeltaZ = 1.0/nHeightSeg

    positions = []
    for i in range(nsides-1, -1, -1):
        positions.append((ppts_top[i][0], ppts_top[i][1], fHeight))
    for i in range(nsides):
        positions.append((ppts_bot[i][0], ppts_bot[i][1], 0.0))
    for i in range(nHeightSeg+1):
        fZ = fDeltaZ*i
        for j in range(nsides+1):
            x = ppts_bot[j][0] + fZ*(ppts_top[j][0]-ppts_bot[j][0])
            y = ppts_bot[j][1] + fZ*(ppts_top[j][1]-ppts_bot[j][1])
            positions.append((x, y, fZ*fHeight))

    top_fan = list(range(0, nsides))
    bot_fan = list(range(nsides, 2*nsides))
    tris = []
    tris.extend(fan_to_tris(top_fan))
    tris.extend(fan_to_tris(bot_fan))
    side_strip = _side_wall_strip(nsides, nHeightSeg, 2*nsides)
    tris.extend(strip_to_tris(side_strip))
    return positions, tris

def create_torus_version(fRatio, nSegs_full, nSides_full, ndet_bias=0):
    nsegs = nSegs_full >> ndet_bias
    nsides = nSides_full >> ndet_bias
    fDeltaTheta = (2*math.pi)/nsegs
    fDeltaPhi = (2*math.pi)/nsides

    positions = []
    for i in range(nsides):
        fPhi = fDeltaPhi*i
        sinPhi, cosPhi = sincos(fPhi)
        fRad = 1.0 + cosPhi*fRatio
        fZ = sinPhi*fRatio
        for j in range(nsegs):
            fTheta = fDeltaTheta*j
            sinT, cosT = sincos(fTheta)
            positions.append((cosT*fRad, sinT*fRad, fZ))

    indices = []
    wVersionStart = 0
    wLoVert = 0
    wHiVert = nsegs
    for i in range(nsides):
        wStripStartLo = wLoVert
        wStripStartHi = wHiVert
        for j in range(nsegs+1):
            indices.append(wLoVert)
            indices.append(wHiVert)
            if j < nsegs-1:
                wLoVert += 1
                wHiVert += 1
            else:
                wLoVert = wStripStartLo
                wHiVert = wStripStartHi
        wLoVert += nsegs
        if (i+1) < (nsides-1):
            wHiVert += nsegs
        else:
            wHiVert = wVersionStart
    tris = strip_to_tris(indices)
    return positions, tris

def create_surf_of_rev_version(pts_with_flags, ax_axis, pt_on_axis, nSegs_full, ndet_bias=0):
    nPts = len(pts_with_flags)
    dwPolyPts = nPts
    for (x,y,z,flags) in pts_with_flags:
        if not (flags & 1):
            dwPolyPts += 1

    pVerts = [None]*dwPolyPts
    ntot = 0
    for i in range(nPts):
        x,y,z,flags = pts_with_flags[i]
        pVerts[ntot] = (x,y,z)
        if not (flags & 1):
            ntot += 1
            pVerts[ntot] = (x,y,z)
        ntot += 1

    nsegs = nSegs_full >> ndet_bias
    fDeltaTheta = (2*math.pi)/nsegs

    positions = []
    for i in range(nsegs+1):
        fTheta = fDeltaTheta*i
        quat = quat_from_axis_angle(ax_axis, fTheta)
        rotMat = rot_from_rh_quat(quat)
        for j in range(dwPolyPts):
            pt = (pVerts[j][0]-pt_on_axis[0], pVerts[j][1]-pt_on_axis[1], pVerts[j][2]-pt_on_axis[2])
            tv = transform_vector(pt, rotMat)
            pos = (tv[0]+pt_on_axis[0], tv[1]+pt_on_axis[1], tv[2]+pt_on_axis[2])
            positions.append(pos)

    indices = []
    wLeftVert = 0
    wRightVert = dwPolyPts
    for i in range(nsegs):
        wStartStripRight = wRightVert
        wStartStripLeft = wLeftVert
        for j in range(dwPolyPts+1):
            indices.append(wRightVert)
            indices.append(wLeftVert)
            if j < dwPolyPts-1:
                wRightVert += 1
                wLeftVert += 1
            else:
                wRightVert = wStartStripRight
                wLeftVert = wStartStripLeft
        wLeftVert = wRightVert
        wRightVert += dwPolyPts
    tris = strip_to_tris(indices)
    return positions, tris

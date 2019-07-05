#!/usr/bin/env python

import numpy as np
from tf.transformations import *

# difference between poses in common frame of structure {'X': np.array([x, y, z]), 'O': np.array(quaternion)}
def pose_diff(p1, p2, k = 1.):
    q1 = p1['O'] 
    q2 = p2['O']
    diff = {'X': k * (p1['X'] - p2['X']), 'O': qq_div(quaternion_slerp(q1, q2, k), q1) }
    return diff

# quaternion rotation
def qv_rot(q, v):
    v = np.append(v, 1)
    return np.matmul(quaternion_matrix(q), v)[0:3]

# quaternion relative rotation
def qq_div(q1, q2):
    return quaternion_multiply(q2, quaternion_inverse(q1))


# angle between two quaternions
def angle(v1, v2, acute):
    angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    if (acute == True):
        return angle
    else:
        return 2 * np.pi - angle

# flat, radial formation with center point in [0 0 0], aligned along x, facing outside
def make_formation(r_form, n):
    r = np.array([r_form, 0., 0.], dtype = np.float64)
    pos = {}
    for i in range(n):
        q_rot = quaternion_from_euler(0, 0,  - 2. * i * np.pi / n)
        pos[i] = {'X': qv_rot(q_rot, r), 'O':q_rot}
    return pos
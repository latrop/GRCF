#! /usr/bin/env python

from math import log10, pi

from numpy import array, linspace
from scipy.special import i0, k0, i1, k1


def flatDiskRotVel(diskCenSurfBri, diskExpScale, scale, Msun, MLratio, distancesKpc):
    angSizeDistance = 206.2648 * scale # MPc
    msun = Msun - 5 + 5 * log10(angSizeDistance*1e6)
    surfDens0Light = 2.512 ** (msun - diskCenSurfBri) / (scale ** 2)  # L sun per square kpc
    surfDens0Mass = 2.08908e-09 * MLratio * surfDens0Light   # kilo per square meter
    G = 6.67e-11 # grav const
    diskExpScaleMeter = diskExpScale * scale * 3.08567e19
    distancesMeter = distancesKpc * 3.08567e19
    y = distancesMeter / (2*diskExpScaleMeter)
    vel_squared = 4*pi * G * surfDens0Mass * diskExpScaleMeter * (y ** 2) * (i0(y)*k0(y) - i1(y)*k1(y))
    return vel_squared

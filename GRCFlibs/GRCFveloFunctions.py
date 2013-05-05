#! /usr/bin/env python

from math import log10, pi

from numpy import array, linspace, arctan
from scipy.special import i0, k0, i1, k1, gamma, gammainc
from scipy.integrate import quad


def flatDiskRotVel(diskCenSurfBri, diskExpScale, scale, Msun, MLratio, distancesKpc):
    if distancesKpc[0] == 0.0:
        distancesKpc[0] = 1e-10
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

def isoHaloRotVel(Rc, V_inf, distancesKpc):
    if distancesKpc[0] == 0.0:
        distancesKpc[0] = 1e-10
    G = 6.67e-11 # grav const
    RcMeters = Rc * 3.08567e19
    distancesMeter = distancesKpc * 3.08567e19
    rho0 = (1e3*V_inf)**2 / (4*pi*G*(RcMeters**2))
    vel_squared = 4*pi*G*rho0*RcMeters**2 * (1-(RcMeters/distancesMeter) * arctan(distancesMeter/RcMeters))
    return vel_squared


def spSymmBulgeRotVel(bulgeEffSurfBri, n, bulgeRe, MLratio, Msun, scale, distancesKpc):
    #            mag/sqarcsec         sec               kpc
    nu_n = 2*n - 1/3. + 4./(405*n) + 46./(25515*n**2)
    angSizeDistance = 206.2648 * scale # MPc
    msun = Msun - 5 + 5 * log10(angSizeDistance*1e6)
    bulgeCenSurfBri = bulgeEffSurfBri - nu_n * 1.085736
    I0 = 2.512 ** (msun - bulgeCenSurfBri) / (scale ** 2)  # L sun per square kpc
    re = bulgeRe * scale # in kpc now
    vel_squared = []
    r0 = re / (nu_n ** n)
    for r in distancesKpc:
        underinteg = lambda x: (x ** 2 / (1 - x**2) ** 0.5) * gammainc(2*n+1, (r/(r0*x))**(1/n)) * gamma(2*n+1)
        m = I0*MLratio * 4 * r0**2 * quad(underinteg, 0, 1)[0] # in solar masses
        vel_squared.append(4.30190777 * m / r)
    return array(vel_squared)
    

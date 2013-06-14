#! /usr/bin/env python

from math import radians, sin

import Tkinter as Tk
import tkFileDialog
from scipy.interpolate import interp1d
from numpy import arange, linspace, abs, array, zeros_like
from numpy import sum as npsum

from GRCFveloFunctions import *

class GalaxyRotation(object):
    def __init__(self, distanceArcSec, velocity, velocity_sigma, scale, mainGraph, canvas):
        self.distanceArcSec = distanceArcSec
        self.velocity = velocity
        self.velocity_obs = velocity
        self.velocity_sigma = velocity_sigma
        self.velocity_obs_sigma = velocity_sigma
        self.scale = scale
        self.distanceKpc = scale * distanceArcSec
        self.bulgeVelocity = zeros_like(velocity)
        self.plotBulge = 0
        self.diskVelocity = zeros_like(velocity)
        self.plotDisk = 0
        self.haloVelocity = zeros_like(velocity)
        self.plotHalo = 0
        self.sumVelocity = zeros_like(velocity)
        self.mainGraph = mainGraph
        self.canvas = canvas
        self.incl = 0
        self.diskChanged = True

    def reScale(self, newscale):
        try:
            newscale = float(newscale)
        except ValueError:
            return False
        if newscale <= 0:
            return False
        self.distanceKpc = self.distanceArcSec * newscale
        self.scale = newscale
        self.plot()

    def deproject(self, newincl):
        try:
            newincl = float(newincl)
        except ValueError:
            return False
        if (newincl <= 0.0) or (newincl > 90.0):
            return False
        self.velocity = self.velocity_obs / sin(radians(newincl))
        self.velocity_sigma = self.velocity_obs_sigma / sin(radians(newincl))
        self.incl = newincl
        self.plot()

    def plot(self):
        a = self.mainGraph.add_subplot(111)
        a.clear()
        a.set_xlabel("Distance [arcsec]")
        a.set_ylabel("Velocity [km/sec]")
        a.errorbar(self.distanceArcSec, self.velocity, self.velocity_sigma, color="k", linestyle="-", label="Observation")
        if self.plotBulge:
            a.plot(self.distanceArcSec, self.bulgeVelocity, color="y", linestyle="--", label="Bulge")
        if self.plotDisk:
            a.plot(self.distanceArcSec, self.diskVelocity, color="r", linestyle="--", label="Disk")
        if self.plotHalo:
            a.plot(self.distanceArcSec, self.haloVelocity, color="b", linestyle="--", label="Halo")
        if self.plotDisk + self.plotHalo+self.plotBulge > 1:
            a.plot(self.distanceArcSec, self.sumVelocity, color="c", linestyle="--", label="Sum")
        if self.plotDisk + self.plotHalo+self.plotBulge >= 1:
            # chi squared value to the plot
            chisq = npsum(((self.velocity-self.sumVelocity)/self.velocity_sigma)**2)
            a.annotate('$\chi^2 = %1.3f$' % (chisq)  , xy=(0.85, -0.09), xycoords='axes fraction')
        maxVelocityAxes = max(max(self.velocity), max(self.sumVelocity)) * 1.1
        a.legend(loc="best", fancybox=True, ncol=2, prop={'size':10})
        a.axis([0, max(self.distanceArcSec)*1.1, 0, maxVelocityAxes])
        a2 = a.twiny()
        a2.clear()
        a2.set_xlabel("Distance [kpc]")
        a2.errorbar(self.distanceKpc, self.velocity, self.velocity_sigma, color="k", linestyle="-", label="Observation")
        a2.axis([0, max(self.distanceKpc)*1.1, 0, maxVelocityAxes])
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
        
    def makeComputation(self, gParams, bParams, dParams, hParams):
        """Compute rotation velocities according to specifued parameters"""
        # Before start store all parameters as object attributes
        self.gParams = gParams
        self.bParams = bParams
        self.dParams = dParams
        self.hParams = hParams
        # check what curves is needed to be plotted
        self.plotBulge = float(bParams["include"])
        self.plotDisk = float(dParams["include"])
        self.plotHalo = float(hParams["include"])
        scale = float(gParams["scale"])
        Msun = float(gParams["Msun"])
        self.sumVelocity = zeros_like(self.velocity)
        if dParams["include"]:
            # compute disk rotation velocity
            diskCenSurfBri = float(dParams["cenSurfBri"])
            diskExpScale = float(dParams["expScale"])
            diskThickness = float(dParams["thickness"])
            diskMLratio = float(dParams["MLratio"])
            if diskThickness == 0.0: # if z is 0 then use simple thin disk model
                diskVelSquared = flatDiskRotVel(diskCenSurfBri,
                                                diskExpScale,
                                                scale,
                                                Msun,
                                                diskMLratio,
                                                self.distanceKpc)
            else: # Thick disc model
                if self.diskChanged: 
                    # if one or more parameters of disk were changed (except M/L ratio)
                    # we have to recompute the whole integral
                    diskVelSquared = thickDiskRotVel(diskCenSurfBri,
                                                     diskExpScale,
                                                     scale,
                                                     Msun,
                                                     diskMLratio,
                                                     diskThickness,
                                                     self.distanceKpc)
                    # store last value of M/L ratio for future fast velocity recomputation
                    self.previousDiskMLratio = diskMLratio
                    self.diskChanged = False
                else:
                    # if only M/L ratio was changed one can compute the new values
                    # of velocity just by rescaling the old values, without
                    # a computation of that big integral
                    diskVelSquared = (diskMLratio / self.previousDiskMLratio) * self.diskVelocity**2 * 1000000
                    self.previousDiskMLratio = diskMLratio
            self.diskVelocity = 0.001 * diskVelSquared ** 0.5
            self.sumVelocity += diskVelSquared
        if hParams["include"]:
            # compute halo rotation velocity
            if hParams["model"] == "isoterm": # isotermal falo
                Rc = float(hParams["firstParam"])
                Vinf = float(hParams["secondParam"])
                haloVelsquared = isoHaloRotVel(Rc, Vinf, self.distanceKpc)
                self.haloVelocity = 0.001 * haloVelsquared ** 0.5
                self.sumVelocity += haloVelsquared
        if bParams["include"]:
            # compude bulge rotation velocity
                bulgeEffSurfBri = float(bParams["effSurfBri"])
                bulgeSersicIndex = float(bParams["sersicIndex"])
                bulgeEffRadius = float(bParams["effRadius"])
                #bulgeOblateness = float(bParams["oblateness"])
                bulgeMLratio = float(bParams["MLratio"])
                if True:# There is no non-spheric bulges yet bulgeOblateness == 1.0: # spherically symmetric bulge
                    bulgeVelSquared = spSymmBulgeRotVel(bulgeEffSurfBri, 
                                                        bulgeSersicIndex, 
                                                        bulgeEffRadius, 
                                                        bulgeMLratio, 
                                                        Msun,
                                                        scale,
                                                        self.distanceKpc)
                    self.bulgeVelocity = 0.001 * bulgeVelSquared ** 0.5
                    self.sumVelocity += bulgeVelSquared

        self.sumVelocity = 0.001 * self.sumVelocity ** 0.5
        self.plot()

    def saveParams(self):
        pass


def getRotationCurve(fname):
    """ Function finds the value of the systematic velocity
    and the location of kinematic center by the velosity curve """
    # read data from file
    distance, velocity, velocity_sigma = [], [], []
    for line in open(fname):
        if line.startswith("#"):
            continue
        distance.append(float(line.split()[0]))
        velocity.append(float(line.split()[1]))
        velocity_sigma.append(float(line.split()[2]))
    # interpolation objects for the velicity and its sigma
    velocity_interp = interp1d(distance, velocity, kind="cubic")
    velocity_sigma_interp = interp1d(distance, velocity_sigma, kind="cubic")
    # Find the true location of the galaxy kinematic center
    chi_sq_min = 1e15
    optimalCenterLocation = 0
    optimalVsys = 0
    x0range = abs(max(distance)) / 20
    drange = abs(max(distance)) / 3
    for x0 in linspace(-x0range, x0range, 50):
        # the corresponding velocity
        Vsys = velocity_interp(x0)
        chi_sq = 0
        for d in linspace(0, drange, 50):
            v_minus = abs(velocity_interp(x0-d)-Vsys)
            v_plus = abs(velocity_interp(x0+d)-Vsys)
            sig = (velocity_sigma_interp(x0-d) + velocity_sigma_interp(x0+d))/2
            chi_sq += (v_minus - v_plus)**2 / sig ** 2
        if chi_sq < chi_sq_min:
            chi_sq_min = chi_sq
            optimalCenterLocation = x0
            optimalVsys = Vsys
    r = []
    v = []
    s = []
    min_d = abs(optimalCenterLocation)
    max_d = min(abs(distance[0]), abs(distance[-1]))-abs(optimalCenterLocation)
    for d in sorted(distance):#linspace(min_d, max_d, len(distance)/2):
        if (d < 0) or (abs(d) > min(abs(distance[0]), abs(distance[-1]))):
            continue
        r.append(d)
        v_minus = abs(velocity_interp(optimalCenterLocation-d)-optimalVsys)
        v_plus = abs(velocity_interp(optimalCenterLocation+d)-optimalVsys)
        v.append((v_minus+v_plus)/2)
        s.append((velocity_sigma_interp(optimalCenterLocation-d)**2 + velocity_sigma_interp(optimalCenterLocation+d)**2)**0.5)
    return array(r), array(v), array(s)


def checAllValues(gParams, bParams, dParams, hParams):
    """ Checking all values for selected components"""
    # 1) Check general parameters:
    try:
        val = float(gParams["incl"])
        if (val<0.0) or (val>90.0):
            return False, "Inclination", "must be between 0 and 90"
    except ValueError:
        return False, "Inclination", "not a number"
    try:
        val = float(gParams["scale"])
        if val <= 0.0:
            return False, "Scale", "must be positive"
    except ValueError:
        return False, "Scale", "not a number"
    try:
        val = float(gParams["Msun"])
    except ValueError:
        return False, "Msun", "not a number"

    # 2) Check bulge params
    if bParams["include"]:
        try:
            val = float(bParams["effSurfBri"])
        except ValueError:
            return False, "Bulge eff.surf.bri", "not a number"
        try:
            val = float(bParams["sersicIndex"])
            if val <= 0.0:
                return False, "Sersic index", "must be positive"
        except ValueError:
            return False, "Sersic index", "not a number"
        try:
            val = float(bParams["effRadius"])
            if val <=0:
                return False, "Bulge eff. radius", "must be positive"
        except ValueError:
            return False, "Bulge eff. radius", "not a number"
#        try:
#            val = float(bParams["oblateness"])
#            if (val<0) or (val>1.0):
#                return False, "Bulge q", "must be between 0 and 1"
#        except ValueError:
#            return False, "Bulge q", "not a number"
        try:
            val = float(bParams["MLratio"])
            if val <= 0.0:
                return False, "Bulge ML", "must be positive"
        except ValueError:
            return False, "Bulge ML", "not a number"
    # 3) check disk params
    if dParams["include"]:
        try:
            val = float(dParams["cenSurfBri"])
        except ValueError:
            return False, "Disk cen.surf.bri", "not a number"
        try:
            val = float(dParams["expScale"])
            if val <= 0.0:
                return False, "Disk h", "must be positive"
        except ValueError:
            return False, "Disk h", "not a number"
        try:
            val = float(dParams["thickness"])
            if val < 0:
                return False, "Disk z", "must be positive"
        except ValueError:
            return False, "Disk z", "not a number"
        try:
            val = float(dParams["MLratio"])
            if val <=0:
                return False, "Disk ML", "must be positive"
        except ValueError:
            return False, "Disk ML", "not a number"
    # 4) check halo params
    if hParams["include"]:
        try:
            val = float(hParams["firstParam"])
        except ValueError:
            return False, "Halo 1st param", "not a number"
        try:
            val = float(hParams["secondParam"])
        except ValueError:
            return False, "Halo 2nd param", "not a number"
    return True, "", ""


def getChiSquared(data, model, sigma):
    return 

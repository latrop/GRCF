#! /usr/bin/env python

from math import radians, sin

import Tkinter as Tk
import tkFileDialog
from scipy.interpolate import interp1d, InterpolatedUnivariateSpline
from numpy import arange, linspace, abs, array, zeros_like, concatenate
from numpy import sum as npsum

from GRCFveloFunctions import *
import time

class GalaxyRotation(object):
    def __init__(self, distanceArcSec, velocity, velocity_sigma, scale, mainGraph, canvas, fileName):
        self.distanceArcSec = distanceArcSec
        self.velocity = velocity
        self.velocity_obs = velocity
        self.velocity_sigma = velocity_sigma
        self.velocity_obs_sigma = velocity_sigma
        self.scale = scale
        self.distanceKpc = scale * distanceArcSec
        self.mainGraph = mainGraph
        self.canvas = canvas
        self.incl = 0
        self.parametersChanged = True
        self.dataFileName = fileName
        self.viewLegend = 1
        self.colouredPaint = 1
        self.previousChiSq = 1e99
        self.showChiSquared = 1
        self.oldHaloParams = {"firstParam":0.0,
                              "secondParam":0.0,
                              "model": None}
        self.oldBulgeParams = {"effSurfBri": 0.0,
                               "sersicIndex": 0.0,
                               "effRadius": 0.0,
                               "MLratio": 0.0}
        self.oldDiskParams = {"cenSurfBri": 0.0,
                              "expScale" : 0.0,
                              "thickness" : 0.0,
                              "MLratio" : 0.0}
        self.oldGeneralParams = {"incl": 0.0,
                                 "scale": 0.0,
                                 "Msun" : 0.0}
        mainStep = (self.distanceArcSec[-1]-self.distanceArcSec[0])/len(distanceArcSec)
        if self.distanceArcSec[0] > self.scale:
            additinal = arange(1, self.distanceArcSec[0], self.scale)
        else:
            additinal = []
        self.distancesToComputeArcSec = concatenate((additinal, self.distanceArcSec))
        print self.distancesToComputeArcSec
        self.distancesToComputeKpc = self.distancesToComputeArcSec * scale
        self.bulgeVelocity = zeros_like(self.distancesToComputeArcSec)
        self.plotBulge = 0
        self.diskVelocity = zeros_like(self.distancesToComputeArcSec)
        self.plotDisk = 0
        self.haloVelocity = zeros_like(self.distancesToComputeArcSec)
        self.plotHalo = 0
        self.sumVelocity = zeros_like(self.distancesToComputeArcSec)


    def reScale(self, newscale):
        try:
            newscale = float(newscale)
        except ValueError:
            return False
        if newscale <= 0:
            return False
        self.distanceKpc = self.distanceArcSec * newscale
        self.distancesToComputeKpc = self.distancesToComputeArcSec * newscale
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
        if self.colouredPaint:
            a.errorbar(self.distanceArcSec, self.velocity, self.velocity_sigma, color="k", linestyle="-", label="Data")
            if self.plotBulge:
                a.plot(self.distancesToComputeArcSec, self.bulgeVelocity, color="m", linestyle=":", label="Bulge")
            if self.plotDisk:
                a.plot(self.distancesToComputeArcSec, self.diskVelocity, color="g", linestyle="--", label="Disk")
            if self.plotHalo:
                a.plot(self.distancesToComputeArcSec, self.haloVelocity, color="b", linestyle="-.", label="Halo")
            if self.plotDisk + self.plotHalo+self.plotBulge > 1:
                a.plot(self.distancesToComputeArcSec, self.sumVelocity, color="r", linestyle="-", label="Sum")
        else:
            a.errorbar(self.distanceArcSec, self.velocity, self.velocity_sigma, color="k", linestyle="-", label="Data", linewidth=2)
            if self.plotBulge:
                a.plot(self.distancesToComputeArcSec, self.bulgeVelocity, color="k", linestyle=":", label="Bulge")
            if self.plotDisk:
                a.plot(self.distancesToComputeArcSec, self.diskVelocity, color="k", linestyle="--", label="Disk")
            if self.plotHalo:
                a.plot(self.distancesToComputeArcSec, self.haloVelocity, color="k", linestyle="-.", label="Halo")
            if self.plotDisk + self.plotHalo+self.plotBulge > 1:
                a.plot(self.distancesToComputeArcSec, self.sumVelocity, color="k", linestyle="-", label="Sum")
        if (self.showChiSquared > 0) and (self.plotDisk + self.plotHalo+self.plotBulge >= 1):
            # chi squared value to the plot
            chisq = self.compute_chi_sq()
            # if this iteration gives a better chi square value, then choose the green color for
            # plot it, if nothing changed -- black, if worse -- red.
            if self.colouredPaint:
                if chisq - self.previousChiSq < -0.0001:
                    chisq_color = "green"
                elif chisq - self.previousChiSq > 0.0001:
                    chisq_color = "red"
                else:
                    chisq_color = "black"
            else:
                chisq_color = "black"
            a.annotate('$\chi^2 = %1.3f$' % (chisq)  , xy=(0.85, -0.09), xycoords='axes fraction', color=chisq_color)
            self.previousChiSq = chisq
        maxVelocityAxes = max(max(self.velocity), max(self.sumVelocity)) * 1.1
        if self.viewLegend == 1:
            a.legend(loc="best", fancybox=True, ncol=2, prop={'size':10})
        a.axis([0, max(self.distanceArcSec)*1.1, 0, maxVelocityAxes])
        a2 = a.twiny()
        a2.clear()
        a2.set_xlabel("Distance [kpc]")
        a2.errorbar(self.distanceKpc, self.velocity, self.velocity_sigma, color="k", linestyle="-", label="Data")
        a2.axis([0, max(self.distanceKpc)*1.1, 0, maxVelocityAxes])
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
        
    def makeComputation(self, gParams, bParams, dParams, hParams, makePlot=True):
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
        incl = float(gParams["incl"])
        scale_old = self.oldGeneralParams["scale"]
        Msun_old = self.oldGeneralParams["Msun"]
        incl_old = self.oldGeneralParams["incl"]
        self.sumVelocity = zeros_like(self.distancesToComputeArcSec)

        if dParams["include"]:
            # compute disk rotation velocity
            diskCenSurfBri = float(dParams["cenSurfBri"])
            diskExpScale = float(dParams["expScale"])
            diskThickness = float(dParams["thickness"])
            diskMLratio = float(dParams["MLratio"])
            diskCenSurfBri_old = self.oldDiskParams["cenSurfBri"]
            diskExpScale_old = self.oldDiskParams["expScale"]
            diskThickness_old = self.oldDiskParams["thickness"]
            diskMLratio_old = self.oldDiskParams["MLratio"]
            # Check if some parameters of the disk was changed
            if ((diskCenSurfBri != diskCenSurfBri_old)
                or (diskExpScale != diskExpScale_old)
                or (diskThickness != diskThickness_old)
                or (scale != scale_old)
                or (Msun != Msun_old)
                or (incl != incl_old)):
                if diskThickness == 0.0: # if z is 0 then use simple thin disk model
                    diskVelSquared = flatDiskRotVel(diskCenSurfBri,
                                                    diskExpScale,
                                                    scale,
                                                    Msun,
                                                    diskMLratio,
                                                    self.distancesToComputeKpc)
                else: # Thick disc model
                    diskVelSquared = thickDiskRotVel(diskCenSurfBri,
                                                     diskExpScale,
                                                     scale,
                                                     Msun,
                                                     diskMLratio,
                                                     diskThickness,
                                                     self.distancesToComputeKpc)
            elif (diskMLratio != diskMLratio_old):
                # if only M/L ratio was changed one can compute the new values
                # of velocity just by rescaling the old values, without
                # a computation of that big integral
                diskVelSquared = (diskMLratio / self.previousDiskMLratio) * self.diskVelocity**2 * 1000000
            else:
                diskVelSquared = self.diskVelocity**2 * 1000000
            # Store new values as new old ones
            self.oldDiskParams["cenSurfBri"] = diskCenSurfBri
            self.oldDiskParams["expScale"] = diskExpScale
            self.oldDiskParams["thickness"] = diskThickness
            self.oldDiskParams["MLratio"] = diskMLratio
            self.previousDiskMLratio = diskMLratio
            self.diskVelocity = 0.001 * diskVelSquared ** 0.5
            self.sumVelocity += diskVelSquared

        if hParams["include"]:
            # compute halo rotation velocity
            if hParams["model"] == "isoterm": # isotermal falo
                Rc = float(hParams["firstParam"])
                Vinf = float(hParams["secondParam"])
                haloVelsquared = isoHaloRotVel(Rc, Vinf, self.distancesToComputeKpc)
                self.haloVelocity = 0.001 * haloVelsquared ** 0.5
                self.sumVelocity += haloVelsquared

        if bParams["include"]:
            # compude bulge rotation velocity
                bulgeEffSurfBri = float(bParams["effSurfBri"])
                bulgeSersicIndex = float(bParams["sersicIndex"])
                bulgeEffRadius = float(bParams["effRadius"])
                bulgeMLratio = float(bParams["MLratio"])
                bulgeEffSurfBri_old = self.oldBulgeParams["effSurfBri"]
                bulgeSersicIndex_old = self.oldBulgeParams["sersicIndex"]
                bulgeEffRadius_old = self.oldBulgeParams["effRadius"]
                bulgeMLratio_old = self.oldBulgeParams["MLratio"]
                # if some parameters of bulge was changes we have to recompute all curve
                if ((bulgeEffSurfBri != bulgeEffSurfBri_old) 
                    or (bulgeSersicIndex != bulgeSersicIndex_old) 
                    or (bulgeEffRadius != bulgeEffRadius_old)
                    or (scale != scale_old)
                    or (Msun != Msun_old)
                    or (incl != incl_old)):
                    bulgeVelSquared = spSymmBulgeRotVel(bulgeEffSurfBri, 
                                                        bulgeSersicIndex, 
                                                        bulgeEffRadius, 
                                                        bulgeMLratio, 
                                                        Msun,
                                                        scale,
                                                        self.distancesToComputeKpc)
                # if only ML ratio was changes we can just rescale old velocity
                elif (bulgeMLratio != bulgeMLratio_old):
                    bulgeVelSquared = (bulgeMLratio / self.previousBulgeMLratio) * self.bulgeVelocity**2 * 1000000
                # If nothing was changed just get old values of velocity
                else:
                    bulgeVelSquared = self.bulgeVelocity**2 * 1000000
                self.bulgeVelocity = 0.001 * bulgeVelSquared ** 0.5
                self.sumVelocity += bulgeVelSquared
                self.previousBulgeMLratio = bulgeMLratio
                # store new values as old ones
                self.oldBulgeParams["effSurfBri"] = bulgeEffSurfBri
                self.oldBulgeParams["sersicIndex"] = bulgeSersicIndex
                self.oldBulgeParams["effRadius"] = bulgeEffRadius
                self.oldBulgeParams["MLratio"] = bulgeMLratio
        self.oldGeneralParams["incl"] = incl
        self.oldGeneralParams["scale"] = scale
        self.oldGeneralParams["Msun"] = Msun
        self.parametersChanged = False
        self.sumVelocity = 0.001 * self.sumVelocity ** 0.5
        if makePlot:
            self.plot()

    def fitBruteForce(self, fitParams):
        t1 = time.time()
        bestChiSq = 1e20
        gParams = self.gParams
        bParams = self.bParams
        dParams = self.dParams
        hParams = self.hParams
        chi_map = []
        if fitParams["bulgeVariate"] > 0:
            bLower = fitParams["bulgeMLlower"]
            bUpper = fitParams["bulgeMLupper"]
        else:
            bLower = bUper = float(bParams["MLratio"])
        if fitParams["diskVariate"] > 0:
            dLower = fitParams["diskMLlower"]
            dUpper = fitParams["diskMLupper"]
        else:
            dLower = dUpper = float(dParams["MLratio"])
        if fitParams["haloVariate"] > 0:
            hLower1 = fitParams["haloFirstlower"]
            hUpper1 = fitParams["haloFirstupper"]
            hLower2 = fitParams["haloSecondlower"]
            hUpper2 = fitParams["haloSecondupper"]
        else:
            hLower1 = hUpper1 = float(hParams["firstParam"])
            hLower2 = hUpper2 = float(hParams["secondParam"])
        for diskML in arange(dLower, dUpper+0.01, 0.1):
            chi_map.append([])
            dParams["MLratio"] = diskML
            for bulgeML in arange(bLower, bUpper+0.01, 0.1):
                bParams["MLratio"] = bulgeML
                chi_map[-1].append([])
                for firstParam in arange(hLower1, hUpper1+0.01, 0.1):
                    hParams["firstParam"] = firstParam
                    for secondParam in arange(hLower2, hUpper2+0.01, 1):
                        hParams["secondParam"] = secondParam
                        self.makeComputation(gParams, bParams, dParams, hParams, makePlot=False)
                        chisq = self.compute_chi_sq()
                        chi_map[-1][-1] = chisq
    #                    if prevChiSq < chisq:
    #                        break
    #                    prevChiSq = chisq
                        if (chisq < bestChiSq) and (chisq < self.previousChiSq):
                            bestChiSq = chisq
                            print bestChiSq
                            self.plot()
                            self.fittedBulgeML = bulgeML
                            self.fittedDiskML = diskML
                            self.fittedHaloFirst = firstParam
                            self.fittedHaloSecond = secondParam
        print time.time() - t1
        return chi_map

    def fitConstantML(self, fitParams):
        t1 = time.time()
        bestChiSq = 1e20
        gParams = self.gParams
        bParams = self.bParams
        dParams = self.dParams
        hParams = self.hParams
        bothLower = fitParams["bothMLlower"]
        bothUpper = fitParams["bothMLupper"]
        if fitParams["haloVariate"] > 0:
            hLower1 = fitParams["haloFirstlower"]
            hUpper1 = fitParams["haloFirstupper"]
            hLower2 = fitParams["haloSecondlower"]
            hUpper2 = fitParams["haloSecondupper"]
        else:
            hLower1 = hUpper1 = float(hParams["firstParam"])
            hLower2 = hUpper2 = float(hParams["secondParam"])
        for bothML in arange(bothLower, bothUpper+0.01, 0.1):
            dParams["MLratio"] = bothML
            bParams["MLratio"] = bothML
            for firstParam in arange(hLower1, hUpper1+0.01, 0.1):
                hParams["firstParam"] = firstParam
                for secondParam in arange(hLower2, hUpper2+0.01, 1):
                    hParams["secondParam"] = secondParam
                    self.makeComputation(gParams, bParams, dParams, hParams, makePlot=False)
                    chisq = self.compute_chi_sq()
#                    if prevChiSq < chisq:
#                        break
#                    prevChiSq = chisq
                    if (chisq < bestChiSq) and (chisq < self.previousChiSq):
                        bestChiSq = chisq
                        print bestChiSq
                        self.plot()
                        self.fittedBulgeML = bothML
                        self.fittedDiskML = bothML
                        self.fittedHaloFirst = firstParam
                        self.fittedHaloSecond = secondParam
        print time.time() - t1

    def compute_chi_sq(self):
        return npsum(((self.velocity-self.sumVelocity[-len(self.velocity):])/self.velocity_sigma)**2)


def getRotationCurve(fname):
    """ Function finds the value of the systematic velocity
    and the location of kinematic center by the velosity curve """
    # read data from file
    distance, velocity, velocity_sigma = [], [], []
    for line in open(fname):
        if line.startswith("#"):
            continue
        if len(line.split()) < 3:
            continue
        distance.append(float(line.split()[0]))
        velocity.append(float(line.split()[1]))
        dv = line.split()[2]
        # some values of velocity dispersion may contain "spline" values
        # so we need to trace this case
        if dv != "spline":
            velocity_sigma.append(float(dv))
        else:
            velocity_sigma.append("spline")
    # Compute an empty velocity sigma values
    if "spline" in velocity_sigma:
        rForFit = []
        sigmaForFit = []
        for i in xrange(len(distance)):
            if velocity_sigma[i] != "spline":
                rForFit.append(distance[i])
                sigmaForFit.append(velocity_sigma[i])
        velocity_sigma_spline = InterpolatedUnivariateSpline(rForFit, sigmaForFit)
        velocity_sigma = velocity_sigma_spline(distance)

    # If systematic velocity was already corrected, then just return rotation curve
    if (distance[0] >= 0.0) and (distance[-1] >= 0.0):
        return array(distance), array(velocity), array(velocity_sigma)
            
    # interpolation objects for the velicity and its sigma
    velocity_interp = interp1d(distance, velocity, kind="cubic")
    velocity_sigma_interp = interp1d(distance, velocity_sigma, kind="cubic")
    # Find the true location of the galaxy kinematic center
    chi_sq_min = 1e15
    optimalCenterLocation = 0
    optimalVsys = 0
    x0range = abs(max(distance)) / 5
    drange = abs(max(distance)) / 2
    for x0 in linspace(-x0range, x0range, 150):
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
        if (optimalCenterLocation - d < min(distance)) or (optimalCenterLocation+d > max(distance)):
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

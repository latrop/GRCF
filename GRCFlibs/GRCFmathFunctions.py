#! /usr/bin/env python

from math import radians, sin

import tkinter as Tk
from tkinter import filedialog as tkFileDialog
from scipy.interpolate import interp1d, InterpolatedUnivariateSpline
from scipy.optimize import fmin as fmin_sco
from scipy.optimize import fmin_tnc
import numpy
from numpy import arange, linspace, abs, array, zeros_like, concatenate, log, zeros
from numpy import sum as npsum

from .wrap_velocity import *
from .GRCFcommonFunctions import fig2img, fig2data
import time

from PIL import Image
from PIL import ImageTk

from copy import copy


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
                               "MLratio": 0.0,
                               "axisRatio": 0.0}
        self.oldDiscParams = {"cenSurfBri": 0.0,
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
        self.distancesToComputeKpc = self.distancesToComputeArcSec * scale
        self.distancesToComputeLength = len(self.distancesToComputeArcSec)
        self.bulgeVelocity = zeros(self.distancesToComputeLength)
        self.plotBulge = 0
        self.discVelocity = zeros(self.distancesToComputeLength)
        self.plotDisc = 0
        self.haloVelocity = zeros(self.distancesToComputeLength)
        self.plotHalo = 0
        self.sumVelocity = zeros(self.distancesToComputeLength)
        self.recomputeHalo = False
        self.optimal_fit_niter = 0
        self.a = self.mainGraph.add_subplot(111)
        self.a2 = self.a.twiny()

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
        if newincl == -1.0: # no correction. just return observed data
            self.velocity = self.velocity_obs
            self.velocity_sigma = self.velocity_obs_sigma
            self.plot()
            return True
        if (newincl <= 0.0) or (newincl > 90.0):
            return False
        self.velocity = self.velocity_obs / sin(radians(newincl))
        self.velocity_sigma = self.velocity_obs_sigma / sin(radians(newincl))
        self.incl = newincl
        self.plot()

    def plot(self):
        self.a.clear()
        #clf()
        #cla()
        self.a.set_xlabel("Distance [arcsec]")
        self.a.set_ylabel("Velocity [km/sec]")
        if self.colouredPaint:
            self.a.errorbar(self.distanceArcSec, self.velocity, self.velocity_sigma,
                            color="k", linestyle="-", label="Data")
            if self.plotBulge:
                self.a.plot(self.distancesToComputeArcSec, self.bulgeVelocity,
                            color="m", linestyle=":", label="Bulge")
            if self.plotDisc:
                self.a.plot(self.distancesToComputeArcSec, self.discVelocity,
                            color="g", linestyle="--", label="Disc")
            if self.plotHalo:
                self.a.plot(self.distancesToComputeArcSec, self.haloVelocity,
                            color="b", linestyle="-.", label="Halo")
            if self.plotDisc + self.plotHalo+self.plotBulge > 1:
                self.a.plot(self.distancesToComputeArcSec, self.sumVelocity,
                            color="r", linestyle="-", label="Sum")
        else:
            self.a.errorbar(self.distanceArcSec, self.velocity, self.velocity_sigma,
                            color="k", linestyle="-", label="Data", linewidth=2)
            if self.plotBulge:
                self.a.plot(self.distancesToComputeArcSec, self.bulgeVelocity,
                            color="k", linestyle=":", label="Bulge")
            if self.plotDisc:
                self.a.plot(self.distancesToComputeArcSec, self.discVelocity,
                            color="k", linestyle="--", label="Disc")
            if self.plotHalo:
                self.a.plot(self.distancesToComputeArcSec, self.haloVelocity,
                            color="k", linestyle="-.", label="Halo")
            if self.plotDisc + self.plotHalo+self.plotBulge > 1:
                self.a.plot(self.distancesToComputeArcSec, self.sumVelocity,
                            color="k", linestyle="-", label="Sum")

        if (self.showChiSquared > 0) and (self.plotDisc + self.plotHalo+self.plotBulge >= 1):
            # chi squared value to the plot
            chisq = self.compute_chi_sq()
            # if this iteration gives a better chi square value, then choose the green color for
            # plot it, if nothing changed -- black, if worse -- red.
            if self.colouredPaint:
                if chisq - self.previousChiSq < -0.000000001:
                    chisq_color = "green"
                elif chisq - self.previousChiSq > 0.000000001:
                    chisq_color = "red"
                else:
                    chisq_color = "black"
            else:
                chisq_color = "black"
            self.a.annotate('$\chi^2 = %1.3f$' % (chisq)  , xy=(0.85, -0.09),
                            xycoords='axes fraction', color=chisq_color)
            self.previousChiSq = chisq

        maxVelocityAxes = max(max(self.velocity), max(self.sumVelocity)) * 1.1
        if self.viewLegend == 1:
            self.a.legend(loc="best", fancybox=True, ncol=2, prop={'size':10})
        self.a.axis([0, max(self.distanceArcSec)*1.1, 0, maxVelocityAxes])
        self.a2.clear()
        #self.a2.cla()
        self.a2.set_xlabel("Distance [kpc]")
        self.a2.errorbar(self.distanceKpc, self.velocity, self.velocity_sigma,
                         color="k", linestyle="-", label="Data")
        self.a2.axis([0, max(self.distanceKpc)*1.1, 0, maxVelocityAxes])
        imageWithGraph = fig2img(self.mainGraph) # store image into PIL object for future usage
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
        return ImageTk.PhotoImage(imageWithGraph)

    def makeComputation(self, gParams, bParams, dParams, hParams, makePlot=True):
        """Compute rotation velocities according to specifued parameters"""
        # Before start store all parameters as object attributes
        self.gParams = gParams
        self.bParams = bParams
        self.dParams = dParams
        self.hParams = hParams
        # check what curves is needed to be plotted
        self.plotBulge = float(bParams["include"])
        self.plotDisc = float(dParams["include"])
        self.plotHalo = float(hParams["include"])
        scale = float(gParams["scale"])
        Msun = float(gParams["Msun"])
        incl = float(gParams["incl"])
        scale_old = self.oldGeneralParams["scale"]
        Msun_old = self.oldGeneralParams["Msun"]
        incl_old = self.oldGeneralParams["incl"]
        self.sumVelocity = zeros_like(self.distancesToComputeArcSec)

        if dParams["include"]:
            # compute disc rotation velocity
            discCenSurfBri = float(dParams["cenSurfBri"])
            discExpScale = float(dParams["expScale"])
            discThickness = float(dParams["thickness"])
            discMLratio = float(dParams["MLratio"])
            discCenSurfBri_old = self.oldDiscParams["cenSurfBri"]
            discExpScale_old = self.oldDiscParams["expScale"]
            discThickness_old = self.oldDiscParams["thickness"]
            discMLratio_old = self.oldDiscParams["MLratio"]

            # Check if some parameters of the disc was changed
            if ((discCenSurfBri != discCenSurfBri_old)
                or (discExpScale != discExpScale_old)
                or (discThickness != discThickness_old)
                or (scale != scale_old)
                or (Msun != Msun_old)
                or (incl != incl_old)):
                t1 = time.time()
                discVelSquared = v_disc(dParams,
                                        gParams,
                                        self.distancesToComputeKpc)
                self.discVelocity = discVelSquared ** 0.5
            elif (discMLratio != discMLratio_old):
                # if only M/L ratio was changed one can compute the new values
                # of velocity just by rescaling the old values, without
                # a computation of that big integral
                discVelSquared = (discMLratio / self.previousDiscMLratio) * self.discVelocity**2
                self.discVelocity = discVelSquared ** 0.5
            else:
                discVelSquared = self.discVelocity**2

            # Store new values as new old ones
            self.oldDiscParams["cenSurfBri"] = discCenSurfBri
            self.oldDiscParams["expScale"] = discExpScale
            self.oldDiscParams["thickness"] = discThickness
            self.oldDiscParams["MLratio"] = discMLratio
            self.previousDiscMLratio = discMLratio
            self.discVelocity = discVelSquared ** 0.5
            self.sumVelocity += discVelSquared

        if bParams["include"]:
            # compude bulge rotation velocity
                bulgeEffSurfBri = float(bParams["effSurfBri"])
                bulgeSersicIndex = float(bParams["sersicIndex"])
                bulgeEffRadius = float(bParams["effRadius"])
                bulgeMLratio = float(bParams["MLratio"])
                bulgeAxisRatio = float(bParams["axisRatio"])
                bulgeEffSurfBri_old = self.oldBulgeParams["effSurfBri"]
                bulgeSersicIndex_old = self.oldBulgeParams["sersicIndex"]
                bulgeEffRadius_old = self.oldBulgeParams["effRadius"]
                bulgeMLratio_old = self.oldBulgeParams["MLratio"]
                bulgeAxisRatio_old = self.oldBulgeParams["axisRatio"]
                # if some parameters of bulge was changes we have to recompute all curve
                if ((bulgeEffSurfBri != bulgeEffSurfBri_old)
                    or (bulgeSersicIndex != bulgeSersicIndex_old)
                    or (bulgeEffRadius != bulgeEffRadius_old)
                    or (scale != scale_old)
                    or (Msun != Msun_old)
                    or (incl != incl_old)
                    or (bulgeAxisRatio != bulgeAxisRatio_old)):
                    bulgeVelSquared = v_bulge(bParams,
                                              dParams,
                                              gParams,
                                              self.distancesToComputeKpc)
                    self.bulgeVelocity = bulgeVelSquared ** 0.5
                # if only ML ratio was changes we can just rescale old velocity
                elif (bulgeMLratio != bulgeMLratio_old):
                    bulgeVelSquared = (bulgeMLratio / self.previousBulgeMLratio) * self.bulgeVelocity**2
                    self.bulgeVelocity = bulgeVelSquared ** 0.5
                # If nothing was changed just get old values of velocity
                else:
                    bulgeVelSquared = self.bulgeVelocity**2
                self.sumVelocity += bulgeVelSquared
                self.previousBulgeMLratio = bulgeMLratio
                # store new values as old ones
                self.oldBulgeParams["effSurfBri"] = bulgeEffSurfBri
                self.oldBulgeParams["sersicIndex"] = bulgeSersicIndex
                self.oldBulgeParams["effRadius"] = bulgeEffRadius
                self.oldBulgeParams["MLratio"] = bulgeMLratio
                self.oldBulgeParams["axisRatio"] = bulgeAxisRatio

        if hParams["include"]:
            # compute halo rotation velocity
            # we have to recompute halo if recompute halo flag is equal 1
            # (wich means that disc or bulge was changed and we have to recompute
            # adiabatic contraction part) or if some halo parameter was changed
            if ((self.recomputeHalo == 1) or
                (self.oldHaloParams["firstParam"] != self.hParams["firstParam"]) or
                (self.oldHaloParams["secondParam"] != self.hParams["secondParam"]) or
                (self.oldHaloParams["model"] != self.hParams["model"]) or
                (self.oldHaloParams["includeAC"] != self.hParams["includeAC"])):
                bParams_copy = bParams.copy()
                dParams_copy = dParams.copy()
                hParams_copy = hParams.copy()
                # if both disc and bulge are switched off, then we can compute halo
                # without adiabatic contraction
                if (not bParams["include"]) and (not dParams["include"]):
                    hParams_copy["includeAC"] = 0
                # if only bulge is switched off, set temporary it's ML ratio to
                # zero such that it will not affect on the adiabatic contraction
                elif not bParams["include"]:
                    bParams_copy["MLratio"] = 0.0
                # the same with the disc
                if not dParams["include"]:
                    dParams_copy["MLratio"] = 0.0
                haloVelsquared = v_halo(bParams_copy,
                                        dParams_copy,
                                        hParams_copy,
                                        gParams,
                                        self.distancesToComputeKpc)
                self.haloVelocity = haloVelsquared ** 0.5
                self.sumVelocity += haloVelsquared
                self.recomputeHalo = False
            else:
                haloVelsquared = self.haloVelocity ** 2.0
                self.sumVelocity += haloVelsquared
            self.oldHaloParams["firstParam"] = hParams["firstParam"]
            self.oldHaloParams["secondParam"] = hParams["secondParam"]
            self.oldHaloParams["model"] = hParams["model"]
            self.oldHaloParams["includeAC"] = hParams["includeAC"]

        self.oldGeneralParams["incl"] = incl
        self.oldGeneralParams["scale"] = scale
        self.oldGeneralParams["Msun"] = Msun
        self.parametersChanged = False
        self.sumVelocity = self.sumVelocity ** 0.5
        if makePlot:
            self.plot()

    def fitBruteForce(self, fitParams):
        bestChiSq = 1e20
        self.previousChiSq = 1e99
        gParams = self.gParams
        bParams = self.bParams
        dParams = self.dParams
        hParams = self.hParams
        # inital best fitting parameters
        self.fittedBulgeML = float(bParams["MLratio"])
        self.fittedDiscML = float(dParams["MLratio"])
        self.fittedHaloFirst = float(hParams["firstParam"])
        self.fittedHaloSecond = float(hParams["secondParam"])
        chi_map = []
        if fitParams["bulgeVariate"] > 0:
            bLower = fitParams["bulgeMLlower"]
            bUpper = fitParams["bulgeMLupper"]
        else:
            bLower = bUpper = float(bParams["MLratio"])
        if fitParams["discVariate"] > 0:
            dLower = fitParams["discMLlower"]
            dUpper = fitParams["discMLupper"]
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
        for discML in arange(dLower, dUpper+0.01, 0.5):
            chi_map.append([])
            dParams["MLratio"] = discML
            for bulgeML in arange(bLower, bUpper+0.01, 0.5):
                bParams["MLratio"] = bulgeML
                chi_map[-1].append([])
                chi_halo_params = []
                for firstParam in arange(hLower1, hUpper1+0.01, 0.25):
                    hParams["firstParam"] = firstParam
                    for secondParam in arange(hLower2, hUpper2+0.01, 5):
                        hParams["secondParam"] = secondParam
                        self.makeComputation(gParams, bParams, dParams, hParams, makePlot=False)
                        chisq = self.compute_chi_sq()
    #                    if prevChiSq < chisq:
    #                        break
    #                    prevChiSq = chisq
                        chi_halo_params.append(chisq)
                        if (chisq < bestChiSq) and (chisq < self.previousChiSq):
                            bestChiSq = chisq
                            self.plot()
                            self.fittedBulgeML = bulgeML
                            self.fittedDiscML = discML
                            self.fittedHaloFirst = firstParam
                            self.fittedHaloSecond = secondParam
                chi_map[-1][-1] = min(chi_halo_params)
        return array(chi_map)

    def fitConstantML(self, fitParams):
        bestChiSq = 1e20
        gParams = self.gParams
        bParams = self.bParams
        dParams = self.dParams
        hParams = self.hParams
        bothLower = fitParams["bothMLlower"]
        bothUpper = fitParams["bothMLupper"]
        fitImproved = False
        chiSqBeforeFit = self.previousChiSq
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
                    if chisq < bestChiSq:
                        if chisq < chiSqBeforeFit:
                            fitImproved = True
                        bestChiSq = chisq
                        self.plot()
                        self.fittedBulgeML = bothML
                        self.fittedDiscML = bothML
                        self.fittedHaloFirst = firstParam
                        self.fittedHaloSecond = secondParam
        return fitImproved


    def fitMaximalDisc(self, fitParams):
        gParams = self.gParams
        bParams = self.bParams
        dParams = self.dParams
        hParams = self.hParams
        # inital best fitting parameters
        self.fittedBulgeML = float(bParams["MLratio"])
        self.fittedDiscML = float(dParams["MLratio"])
        self.fittedHaloFirst = float(hParams["firstParam"])
        self.fittedHaloSecond = float(hParams["secondParam"])
        if fitParams["bulgeVariate"] > 0:
            bLower = fitParams["bulgeMLlower"]
            bUpper = fitParams["bulgeMLupper"]
        else:
            bLower = bUpper = float(bParams["MLratio"])
        if fitParams["discVariate"] > 0:
            dLower = fitParams["discMLlower"]
            dUpper = fitParams["discMLupper"]
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
        chi_sqList = []
        bhOptimalList = [] # parameters of bulge end halo wich lead to minimum of chi sq. for given disc ML ratio
        plotList = [] # list of graphs with optimal fitting values for given disc ML ratio
        for discML in arange(dLower, dUpper+0.01, 0.1):
            bestChiSq = 1e20
            dParams["MLratio"] = discML
            for bulgeML in arange(bLower, bUpper+0.01, 0.1):
                bParams["MLratio"] = bulgeML
                for firstParam in arange(hLower1, hUpper1+0.01, 0.1):
                    hParams["firstParam"] = firstParam
                    for secondParam in arange(hLower2, hUpper2+0.01, 1):
                        hParams["secondParam"] = secondParam
                        self.makeComputation(gParams, bParams, dParams, hParams, makePlot=False)
                        chisq = self.compute_chi_sq()
                        if (chisq < bestChiSq):
                            bestChiSq = chisq
                            fittedBulgeML = bulgeML
                            fittedHaloFirst = firstParam
                            fittedHaloSecond = secondParam
            # make plot for optimal fitting parameters for given disc ML ratio
            bParams["MLratio"] = fittedBulgeML
            hParams["firstParam"] = fittedHaloFirst
            hParams["secondParam"] = fittedHaloSecond
            self.makeComputation(gParams, bParams, dParams, hParams, makePlot=False)
            fittedGraph = self.plot()
            # store all chi squared, optimal parameters and plots of optimal configurations
            chi_sqList.append(bestChiSq)
            bhOptimalList.append([fittedBulgeML, fittedHaloFirst, fittedHaloSecond])
            plotList.append(fittedGraph)
        return bhOptimalList, plotList


    def fitMaximalDisc2(self, fitParams):
        gParams = self.gParams
        bParams = self.bParams
        dParams = self.dParams
        hParams = self.hParams
        dLower = fitParams["discMLlower"]
        dUpper = fitParams["discMLupper"]
        # inital best fitting parameters
        self.fittedBulgeML = float(bParams["MLratio"])
        self.fittedDiscML = float(dParams["MLratio"])
        self.fittedHaloFirst = float(hParams["firstParam"])
        self.fittedHaloSecond = float(hParams["secondParam"])
        chi_sqList = []
        bhOptimalList = [] # parameters of bulge end halo wich lead to minimum of chi sq. for given disc ML ratio
        plotList = [] # list of graphs with optimal fitting values for given disc ML ratio
        for discML in arange(dLower, dUpper+0.01, 0.1):
            bestChiSq = 1e20
            dParams["MLratio"] = discML

            def func(x): # we are going to minimize this function
                """this function runs computation of rotation curve with given parameters
                and returns chi squared. Variable x expands as [MLbulge, MLdisc, h1, h2]"""
                MLbulge = x[0]
                haloFirst = x[1]
                haloSecond = x[2]
                if (MLbulge < 0.1) or (haloFirst < 0.01) or (haloSecond < 0.1): # negative parameters are impossible
                    return 1e99
                # get all model params
                gParams = self.gParams     #
                bParams = self.bParams     # may be this function will work without theese lines
                dParams = self.dParams     #
                hParams = self.hParams     #
                # modify fitting params
                bParams["MLratio"] = MLbulge
                hParams["firstParam"] = haloFirst
                hParams["secondParam"] = haloSecond
                # compute new curve
                self.makeComputation(gParams, bParams, dParams, hParams, makePlot=False)
                # return chi squared
                return self.compute_chi_sq()
            # guess parameters are last cumputed fitting parameters
            MLbulge0 = self.bParams["MLratio"]
            haloFirst0 = self.hParams["firstParam"]
            haloSecond0 = self.hParams["secondParam"]
            # run local minimum finding
            xopt, fopt, ite, funcalls, warnflag = fmin_sco(func, x0=[MLbulge0, haloFirst0, haloSecond0], full_output=1)
            MLbulgeOpt, haloFirstOpt, haloSecondOpt = xopt[0], xopt[1], xopt[2]
            # make plot for optimal fitting parameters for given disc ML ratio
            bParams["MLratio"] = MLbulgeOpt
            hParams["firstParam"] = haloFirstOpt
            hParams["secondParam"] = haloSecondOpt
            self.makeComputation(gParams, bParams, dParams, hParams, makePlot=False)
            fittedGraph = self.plot()
            # store all optimal parameters and plots of optimal configurations
            bhOptimalList.append([MLbulgeOpt, haloFirstOpt, haloSecondOpt])
            plotList.append(fittedGraph)
        return bhOptimalList, plotList


    def fitOptimal(self, bounds):
        self.optimal_fit_niter = 0
        def func(x): # we are going to minimize this function
            """this function runs computation of rotation curve with given parameters
            and returns chi squared. Variable x expands as [MLbulge, MLdisc, h1, h2]"""
            self.optimal_fit_niter += 1
            MLbulge = x[0]
            MLdisc = x[1]
            haloFirst = x[2]
            haloSecond = x[3]
            # get all model params
            gParams = self.gParams
            bParams = self.bParams
            dParams = self.dParams
            hParams = self.hParams
            # modify fitting params
            bParams["MLratio"] = MLbulge
            dParams["MLratio"] = MLdisc
            hParams["firstParam"] = haloFirst
            hParams["secondParam"] = haloSecond
            # compute new curve
            if dParams["MLratio"] < 0.1:
                return 1e15
            self.makeComputation(gParams,
                                 bParams,
                                 dParams,
                                 hParams,
                                 makePlot=(self.optimal_fit_niter%10==0))
            # return chi squared
            return self.compute_chi_sq()
        # guess parameters are last cumputed fitting parameters
        MLbulge0 = self.bParams["MLratio"]
        MLdisc0 = self.dParams["MLratio"]
        haloFirst0 = self.hParams["firstParam"]
        haloSecond0 = self.hParams["secondParam"]
        # run local minimum finding
        xopt, nfeval, rc = fmin_tnc(func,
                                    x0=[MLbulge0, MLdisc0, haloFirst0, haloSecond0],
                                    approx_grad = True,
                                    bounds=bounds)
        MLbulgeOpt, MLdiscOpt, haloFirstOpt, haloSecondOpt = xopt[0], xopt[1], xopt[2], xopt[3]
        # plot resulting curve
        self.plot()
        return MLbulgeOpt, MLdiscOpt, haloFirstOpt, haloSecondOpt


    def compute_chi_sq(self):
        return numpy.nansum(((self.velocity-self.sumVelocity[-len(self.velocity):])/self.velocity_sigma)**2)


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
        for i in range(len(distance)):
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
            new_value = (v_minus - v_plus)**2 / sig ** 2
            if numpy.isfinite(new_value):
                chi_sq += new_value
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
    if int(gParams["iCorrect"]) != 0:
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
        try:
            qb = float(bParams["axisRatio"])
            qd = float(dParams["axisRatio"])
            if qb < qd:
                return False, "Bulge axis ratio", "must be greater than the axis ratio of the disc"
        except:
            return False, "Bulge or disc axis ratio", "not a number"
    # 3) check disc params
    if dParams["include"]:
        try:
            val = float(dParams["cenSurfBri"])
        except ValueError:
            return False, "Disc cen.surf.bri", "not a number"
        try:
            val = float(dParams["expScale"])
            if val <= 0.0:
                return False, "Disc h", "must be positive"
        except ValueError:
            return False, "Disc h", "not a number"
        try:
            val = float(dParams["thickness"])
            if val < 0:
                return False, "Disc z", "must be positive"
        except ValueError:
            return False, "Disc z", "not a number"
        try:
            val = float(dParams["MLratio"])
            if val <=0:
                return False, "Disc ML", "must be positive"
        except ValueError:
            return False, "Disc ML", "not a number"
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

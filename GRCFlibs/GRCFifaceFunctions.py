#! /usr/bin/env python

import os
import Tkinter as Tk
import tkFileDialog, tkMessageBox
import shelve
import time

from scipy.odr.odrpack import *
from scipy.ndimage import minimum_position

from pylab import *
import pylab

import Image
from PIL import ImageTk

from GRCFcommonFunctions import fig2img, fig2data

def fitByLine(xxx, yyy):
    f = lambda B, x: B[0]*x + B[1]
    fitting = ODR(RealData(xxx, yyy), 
                  Model(f), 
                  [-1.0, 0])
    fitting.set_job()
    result = fitting.run()
    return result.beta[0], result.beta[1]

def geomLine(B, x):
    return B[0]*x +B[1]

def mouse_wheel_up(event):
    try:
        oldvalue = float(event.widget.get())
    except ValueError:
        return None
    newvalue = str(oldvalue+0.1)
    event.widget.setvar(name=event.widget.cget("textvariable"), value=newvalue)

def mouse_wheel_down(event):
    try:
        oldvalue = float(event.widget.get())
    except ValueError:
        return None
    newvalue = str(oldvalue-0.1)
    event.widget.setvar(name=event.widget.cget("textvariable"), value=newvalue)


def onoffPanel(panel, newstate):
    if newstate:
        for c in panel.winfo_children():
            if c.winfo_class() in ("Entry", "Radiobutton", "Spinbox"):
                c.config(state="normal")
    else:
        for c in panel.winfo_children():
            if c.winfo_class() in ("Entry", "Radiobutton", "Spinbox"):
                c.config(state="disabled")


###### List of passbands for solar absolute magnitudes #######
mSunBandsList = ["Buser U (= Johnson) Vega",
                 "Buser U (= Johnson) AB",
                 "Straizys B (= Johnson) Vega",
                 "Straizys B (= Johnson) AB",
                 "Straizys V (= Johnson) Vega",
                 "Straizys V (= Johnson) AB",
                 "Bessell R Vega",
                 "Bessell R AB",
                 "Bessell I Vega",
                 "Bessell I AB",
                 "SDSS u' Vega",
                 "SDSS u' AB",
                 "SDSS g' Vega",
                 "SDSS g' AB",
                 "SDSS r' Vega",
                 "SDSS r' AB",
                 "SDSS i' Vega",
                 "SDSS i' AB",
                 "SDSS z' Vega",
                 "SDSS z' AB"
                 ]

mSunBands = {"Buser U (= Johnson) Vega": 5.59,
             "Buser U (= Johnson) AB": 6.32,
             "Straizys B (= Johnson) Vega": 5.45,
             "Straizys B (= Johnson) AB": 5.36,
             "Straizys V (= Johnson) Vega": 4.78,
             "Straizys V (= Johnson) AB": 4.79,
             "Bessell R Vega": 4.46,
             "Bessell R AB": 4.65,
             "Bessell I Vega": 4.11,
             "Bessell I AB": 4.55,
             "SDSS u' Vega": 5.46,
             "SDSS u' AB": 6.45,
             "SDSS g' Vega": 5.22,
             "SDSS g' AB": 5.14,
             "SDSS r' Vega": 4.50,
             "SDSS r' AB": 4.65,
             "SDSS i' Vega": 4.16,
             "SDSS i' AB": 4.56,
             "SDSS z' Vega": 4.01,
             "SDSS z' AB": 4.52
             }

# 	filter	Vega	AB
#6 	F300W 	6.09 	7.52
#7 	F450W 	5.32 	5.25
#8 	F555W 	4.85 	4.85
#9 	F606W 	4.66 	4.75
#10 	F702W 	4.32 	4.58
#11 	F814W 	4.15 	4.57
#12 	CFHT U 	5.57 	6.38
#13 	CFHT B 	5.49 	5.32
#14 	CFHT V 	4.81 	4.81
#15 	CFHT R 	4.44 	4.64
#16 	CFHT I 	4.06 	4.54
#17 	KPNO U 	5.59 	6.32
#18 	KPNO B 	5.49 	5.43
#19 	KPNO V 	4.79 	4.79
#20 	KPNO R 	4.47 	4.66
#21 	KPNO I 	4.11 	4.55
# 22 	Koo & Kron U 	5.58 	6.29
# 23 	Koo & Kron J 	5.31 	5.26
# 24 	Koo & Kron F 	4.58 	4.69
# 25 	Koo & Kron N 	4.11 	4.53
# 31 	ACS old z 	3.99 	4.52
# 32 	FIS555 	4.84 	4.84
# 33 	FIS606 	4.63 	4.72
# 34 	FIS702 	4.32 	4.59
# 35 	FIS814 	4.12 	4.53
# 36 	LRIS B 	5.46 	5.42
# 37 	LRIS V 	4.82 	4.83
# 38 	LRIS R 	4.46 	4.63
# 39 	LRIS Rs 	4.33 	4.59
# 40 	LRIS I 	4.04 	4.53
# 41 	LRIS Z 	4.00 	4.52
# 42 	SPH Un 	5.43 	6.49
# 43 	SPH G 	5.21 	5.11
# 44 	SPH Rs 	4.39 	4.61
# 45 	12k B 	5.45 	5.34
# 46 	12k R 	4.39 	4.60
# 47 	12k I 	4.10 	4.53
# 48 	12k V 	4.85 	4.85
# 49 	uh8K i 	4.06 	4.53
# 50 	ACS B435 	5.49 	5.40
# 51 	ACS V606 	4.67 	4.75
# 52 	ACS SDSS i 	4.14 	4.54
# 53 	ACS I814 	4.11 	4.53
# 54 	ACS SDSS z 	4.00 	4.52
# 55 	Bessell U 	5.55 	6.36
# 56 	Bessell B 	5.45 	5.36
# 57 	Bessell V 	4.80 	4.82
# 58 	Bessell J 	3.67 	4.57
# 59 	Bessell H 	3.33 	4.71
# 60 	Bessell K 	3.29 	5.19
# 61 	KPNO J 	3.66 	4.57
# 62 	KPNO H 	3.33 	4.71
# 63 	KPNO K 	3.29 	5.18
# 64 	2500 	7.96 	9.80
# 65 	2800 	6.67 	8.23
# 66 	APM Bj 	5.29 	5.21
# 67 	FOCA UV 	10.50 	12.39
# 68 	DEIMOS R 	4.44 	4.62 
# 69 	Galex FUV 	13.97 	16.42
# 70 	Galex NUV 	8.45 	10.31
# 71 	SDSS u z=0.1 	5.83 	6.77
# 72 	SDSS g z=0.1 	5.46 	5.36
# 73 	SDSS r z=0.1 	4.53 	4.67
# 74 	SDSS i z=0.1 	4.12 	4.48
# 75 	SDSS z z=0.1 	3.90 	4.42
# 76 	NIRI J 	3.64 	4.57
# 77 	NIRI H 	3.33 	4.71
# 78 	NIRI K 	3.29 	5.18

def saveParams(master, params):
    """Store all parameters of galaxy in a file"""
    fileName = tkFileDialog.asksaveasfilename(parent=master,
                                              filetypes=[("Data Base files", "*.db")],
                                              title="Open file to save parameters")
    if not fileName:
        return
    try:
        os.remove(fileName)
    except OSError:
        pass
    gParams = params[0]
    bParams = params[1]
    dParams = params[2]
    hParams = params[3]
    dataBase = shelve.open(fileName)
    dataBase["gParams"] = gParams
    dataBase["bParams"] = bParams
    dataBase["dParams"] = dParams
    dataBase["hParams"] = hParams
    dataBase.close()

def loadParams(master):
    """Load prevoiusly saved parameters from file"""
    fileName = tkFileDialog.askopenfilename(parent=master,
                                            filetypes=[("Data Base files", "*.db")],
                                            title="Open file to load parameters")
    if not fileName:
        return [None, None, None, None]
    dataBase = shelve.open(fileName)
    gParams = dataBase["gParams"]
    bParams = dataBase["bParams"]
    dParams = dataBase["dParams"]
    hParams = dataBase["hParams"]
    dataBase.close()
    return gParams, bParams, dParams, hParams


def saveVelocity(master, rotCurve):
    if rotCurve.parametersChanged:
        tkMessageBox.showerror("Save error", "Some parameters was changed.\nRun computation and try again.")
        return
    """Save all computed velocity curves (and the observed one) to a text file"""
    fileName = tkFileDialog.asksaveasfilename(parent=master,
                                              filetypes=[("Data files", "*.dat"),
                                                         ("Text files", "*.txt"),
                                                         ("Velocity files", "*.vel")],
                                              title="Open file to save velocity curves")
    if not fileName:
        return
    fout = open(fileName, "w", buffering=0)
    fout.truncate(0)
    includeBulge = int(rotCurve.bParams["include"])
    includeDisk = int(rotCurve.dParams["include"])
    includeHalo = int(rotCurve.hParams["include"])
    delimeter = "#" * 40
    fout.write("%s\n#\n" % (delimeter))
    fout.write("# File generated by GRCF programm (see...) \n# at %s\n#\n" % time.ctime())
    fout.write("# Input data file is %s \n#\n" % os.path.split(rotCurve.dataFileName)[1])
    fout.write("# Parameters are:\n")
    fout.write("#               scale = %s\n" % (rotCurve.gParams["scale"]))
    fout.write("#               H0 = %s\n" % (rotCurve.gParams["hubble"]))
    fout.write("#               Msun = %s\n" % (rotCurve.gParams["Msun"]))
    fout.write("#\n")
    fout.write("# Parameters of bulge:\n")
    if includeBulge == 1:
        fout.write("#               eff. surf. bri. = %s\n" % (rotCurve.bParams["effSurfBri"]))
        fout.write("#               Sersic index = %s\n" % (rotCurve.bParams["sersicIndex"]))
        fout.write("#               eff radius = %s\n" % (rotCurve.bParams["effRadius"]))
        fout.write("#               axis ratio = %s\n" % (rotCurve.bParams["axisRatio"]))
        fout.write("#               M/L ratio = %s\n" % (rotCurve.bParams["MLratio"]))
    else:
        fout.write("#               bulge is not included\n")
    fout.write("#\n")
    fout.write("# Parameters of disk:\n")
    if includeDisk == 1:
        fout.write("#               cent. surf. bri. = %s\n" % (rotCurve.dParams["cenSurfBri"]))
        fout.write("#               exp. scale = %s\n" % (rotCurve.dParams["expScale"]))
        fout.write("#               axis ratio = %s\n" % (rotCurve.dParams["axisRatio"]))
        fout.write("#               h/z0 = %s\n" % (rotCurve.dParams["thickness"]))
        fout.write("#               M/L ratio = %s\n" % (rotCurve.dParams["MLratio"]))
    else:
        fout.write("#               disk is not included\n")
    fout.write("#\n")
    fout.write("# Parameters of halo:\n")
    if includeHalo == 1:
        if rotCurve.hParams["model"] == "isoterm":
            firstParName = "Rc"
            secondParName = "V(inf)"
        else:
            firstParName = "C"
            secondParName = "V200"
        fout.write("#               model = %s\n" % (rotCurve.hParams["model"]))
        fout.write("#               %s = %s\n" % (firstParName, rotCurve.hParams["firstParam"]))
        fout.write("#               %s = %s\n" % (secondParName, rotCurve.hParams["secondParam"]))
    else:
        fout.write("#               halo is not included\n")
    fout.write("#\n")
    fout.write("#R[arcsec]   R[kpc]   vObs       +/-     vBulge    vDisk      vHalo      vSum\n")
    obs_counter = 0
    for i in xrange(len(rotCurve.distancesToComputeKpc)):
        fout.write("%6.1f    " % (rotCurve.distancesToComputeArcSec[i]))
        fout.write("%7.3f   " % (rotCurve.distancesToComputeKpc[i]))
        if rotCurve.distancesToComputeKpc[i] > rotCurve.distanceKpc[0]:
            fout.write("%7.2f   " % (rotCurve.velocity[obs_counter]))
            fout.write("%7.2f   " % (rotCurve.velocity_sigma[obs_counter]))
            obs_counter += 1
        else:
            fout.write(" ------   ")
            fout.write(" ------   ")
        if includeBulge:
            fout.write("%7.2f   " % (rotCurve.bulgeVelocity[i]))
        else:
            fout.write("------    ")
        if includeDisk:
            fout.write("%7.2f   " % (rotCurve.diskVelocity[i]))
        else:
            fout.write("------    ")
        if includeHalo:
            fout.write("%7.2f   " % (rotCurve.haloVelocity[i]))
        else:
            fout.write("------   ")
        fout.write("%7.2f\n" %  (rotCurve.sumVelocity[i]))
    fout.close()


class BruteForceWindow(object):
    def __init__(self,
                 master,
                 rotCurve,
                 includeBulge,
                 includeDisk,
                 includeHalo,
                 bulgeMLratioValue,
                 diskMLratioValue,
                 haloFirstParamValue,
                 haloSecondParamValue):
        self.bulgeMLratioValue = bulgeMLratioValue
        self.diskMLratioValue = diskMLratioValue
        self.haloFirstParamValue = haloFirstParamValue
        self.haloSecondParamValue = haloSecondParamValue
        self.rotCurve = rotCurve
        self.bruteForceFrame = Tk.Toplevel(takefocus=True)
        self.bruteForceFrame.wm_attributes("-topmost", 1)
        self.bruteForceFrame.grab_set()
        xScreenSize = master.winfo_screenwidth()
        yScreenSize = master.winfo_screenheight()
        self.bruteForceFrame.geometry("+%i+%i" % (xScreenSize/2-250, yScreenSize/2-100))
        Tk.Label(self.bruteForceFrame, text="Chose models and ranges to variate:").grid(column=0, row=0, columnspan=5)
        self.bulgeState = "normal" if includeBulge else "disabled"
        self.diskState = "normal" if includeDisk else "disabled"
        self.haloState = "normal" if includeHalo else "disabled"

        # Bulge parameters
        self.variateBulge = Tk.IntVar()
        self.variateBulgeCButton = Tk.Checkbutton(self.bruteForceFrame, variable=self.variateBulge, text="Bulge:", state=self.bulgeState)
        self.variateBulgeCButton.grid(column=0, row=1)
        Tk.Label(self.bruteForceFrame, text="M-to-L  from").grid(column=1, row=1)
        self.bulgeMLlowerValue = Tk.StringVar()
        self.bulgeMLlowerValue.set(self.rotCurve.bParams["MLratio"])
        self.bulgeMLlowerEntry = Tk.Spinbox(self.bruteForceFrame,
                                            textvariable=self.bulgeMLlowerValue, 
                                            width=5, 
                                            bg="white",
                                            from_=0.0,
                                            to=100,
                                            increment=0.1,
                                            state=self.bulgeState)
        self.bulgeMLlowerEntry.grid(column=2, row=1)
        if self.diskState == "normal":
            self.bulgeMLlowerEntry.bind("<Button-4>", mouse_wheel_up)
            self.bulgeMLlowerEntry.bind("<Button-5>", mouse_wheel_down)
        Tk.Label(self.bruteForceFrame, text=" to ").grid(column=3, row=1)
        self.bulgeMLupperValue = Tk.StringVar()
        self.bulgeMLupperValue.set(self.rotCurve.bParams["MLratio"])
        self.bulgeMLupperEntry = Tk.Spinbox(self.bruteForceFrame,
                                            textvariable=self.bulgeMLupperValue,
                                            width=5,
                                            bg="white",
                                            from_=0.0,
                                            to=100,
                                            increment=0.1, 
                                            state=self.bulgeState)
        self.bulgeMLupperEntry.grid(column=4, row=1)
        if self.bulgeState == "normal":
            self.bulgeMLupperEntry.bind("<Button-4>", mouse_wheel_up)
            self.bulgeMLupperEntry.bind("<Button-5>", mouse_wheel_down)

        # Disk parameters
        self.variateDisk = Tk.IntVar()
        self.variateDiskCButton = Tk.Checkbutton(self.bruteForceFrame, variable=self.variateDisk, text=" Disk: ", state=self.diskState)
        self.variateDiskCButton.grid(column=0, row=2)

        Tk.Label(self.bruteForceFrame, text="M-to-L  from").grid(column=1, row=2)
        self.diskMLlowerValue = Tk.StringVar()
        self.diskMLlowerValue.set(self.rotCurve.dParams["MLratio"])
        self.diskMLlowerEntry = Tk.Spinbox(self.bruteForceFrame,
                                           textvariable=self.diskMLlowerValue,
                                           width=5,
                                           bg="white",
                                           from_=0.0,
                                           to=100,
                                           increment=0.1, 
                                           state=self.diskState)
        self.diskMLlowerEntry.grid(column=2, row=2)
        if self.diskState == "normal":
            self.diskMLlowerEntry.bind("<Button-4>", mouse_wheel_up)
            self.diskMLlowerEntry.bind("<Button-5>", mouse_wheel_down)
        Tk.Label(self.bruteForceFrame, text=" to ").grid(column=3, row=2)
        self.diskMLupperValue = Tk.StringVar()
        self.diskMLupperValue.set(self.rotCurve.dParams["MLratio"])
        self.diskMLupperEntry = Tk.Spinbox(self.bruteForceFrame,
                                           textvariable=self.diskMLupperValue,
                                           width=5, 
                                           bg="white", 
                                           from_=0.0,
                                           to=100,
                                           increment=0.1,
                                           state=self.diskState)
        self.diskMLupperEntry.grid(column=4, row=2)
        if self.diskState == "normal":
            self.diskMLupperEntry.bind("<Button-4>", mouse_wheel_up)
            self.diskMLupperEntry.bind("<Button-5>", mouse_wheel_down)

        # Halo
        self.variateHalo = Tk.IntVar()
        self.variateHaloCButton = Tk.Checkbutton(self.bruteForceFrame, variable=self.variateHalo, text=" Halo: ", state=self.haloState)
        self.variateHaloCButton.grid(column=0, row=3, rowspan=2)

        if self.rotCurve.hParams["model"] == "isoterm":
            Tk.Label(self.bruteForceFrame, text="Rc  from").grid(column=1, row=3)
        elif self.rotCurve.hParams["model"] == "NFW":
            Tk.Label(self.bruteForceFrame, text="C  from").grid(column=1, row=3)
        self.haloFirstlowerValue = Tk.StringVar()
        self.haloFirstlowerValue.set(self.rotCurve.hParams["firstParam"])
        self.haloFirstlowerEntry = Tk.Spinbox(self.bruteForceFrame,
                                              textvariable=self.haloFirstlowerValue,
                                              width=5,
                                              bg="white",
                                              from_=0.0,
                                              to=100,
                                              increment=0.1,
                                              state=self.haloState)
        self.haloFirstlowerEntry.grid(column=2, row=3)
        if self.haloState == "normal":
            self.haloFirstlowerEntry.bind("<Button-4>", mouse_wheel_up)
            self.haloFirstlowerEntry.bind("<Button-5>", mouse_wheel_down)
        Tk.Label(self.bruteForceFrame, text=" to ").grid(column=3, row=3)
        self.haloFirstupperValue = Tk.StringVar()
        self.haloFirstupperValue.set(self.rotCurve.hParams["firstParam"])
        self.haloFirstupperEntry = Tk.Spinbox(self.bruteForceFrame,
                                              textvariable=self.haloFirstupperValue,
                                              width=5, 
                                              bg="white", 
                                              from_=0.0,
                                              to=100,
                                              increment=0.1,
                                              state=self.haloState)
        self.haloFirstupperEntry.grid(column=4, row=3)
        if self.haloState == "normal":
            self.haloFirstupperEntry.bind("<Button-4>", mouse_wheel_up)
            self.haloFirstupperEntry.bind("<Button-5>", mouse_wheel_down)

        if self.rotCurve.hParams["model"] == "isoterm":
            Tk.Label(self.bruteForceFrame, text="V(inf)  from").grid(column=1, row=4)
        elif self.rotCurve.hParams["model"] == "NFW":
            Tk.Label(self.bruteForceFrame, text="V200  from").grid(column=1, row=4)
        self.haloSecondlowerValue = Tk.StringVar()
        self.haloSecondlowerValue.set(self.rotCurve.hParams["secondParam"])
        self.haloSecondlowerEntry = Tk.Spinbox(self.bruteForceFrame,
                                               textvariable=self.haloSecondlowerValue,
                                               width=5,
                                               bg="white",
                                               from_=0.0,
                                               to=1000,
                                               increment=1.0,
                                               state=self.haloState)
        self.haloSecondlowerEntry.grid(column=2, row=4)
        if self.haloState == "normal":
            self.haloSecondlowerEntry.bind("<Button-4>", mouse_wheel_up)
            self.haloSecondlowerEntry.bind("<Button-5>", mouse_wheel_down)
        Tk.Label(self.bruteForceFrame, text=" to ").grid(column=3, row=4)
        self.haloSecondupperValue = Tk.StringVar()
        self.haloSecondupperValue.set(self.rotCurve.hParams["secondParam"])
        self.haloSecondupperEntry = Tk.Spinbox(self.bruteForceFrame,
                                               textvariable=self.haloSecondupperValue,
                                               width=5, 
                                               bg="white", 
                                               from_=0.0,
                                               to=1000,
                                               increment=1.0,
                                               state=self.haloState)
        self.haloSecondupperEntry.grid(column=4, row=4)
        if self.haloState == "normal":
            self.haloSecondupperEntry.bind("<Button-4>", mouse_wheel_up)
            self.haloSecondupperEntry.bind("<Button-5>", mouse_wheel_down)

        # Buttons
        self.runButton = Tk.Button(self.bruteForceFrame, text="Run", state="normal", command=self.run)
        self.runButton.grid(column=0, row=6)
        self.saveButton = Tk.Button(self.bruteForceFrame, text="Save", state="disabled", command=self.save_fitted)
        self.saveButton.grid(column=1, row=6)
        self.cancelButton = Tk.Button(self.bruteForceFrame,
                                      text="Close",
                                      state="normal",
                                      command=lambda: self.bruteForceFrame.destroy())
        self.cancelButton.grid(column=4, row=6)
        self.mapButton = Tk.Button(self.bruteForceFrame, text="Map", state="disabled", command=self.show_map)
        self.mapButton.grid(column=2, row=6)
        self.runLabelValue = Tk.StringVar()
        Tk.Label(self.bruteForceFrame, textvariable=self.runLabelValue).grid(column=1, row=5, columnspan=3)

    def run(self):
        if self.variateBulge.get() and ((float(self.bulgeMLlowerValue.get()) > float(self.bulgeMLupperValue.get()))
                                        or (float(self.bulgeMLlowerValue.get())<=0)):
            self.runLabelValue.set("Error in bulge parameters")
            return 1
        if self.variateDisk.get() and ((float(self.diskMLlowerValue.get()) > float(self.diskMLupperValue.get()))
                                        or (float(self.diskMLlowerValue.get())<=0)):
            self.runLabelValue.set(" Error in disk parameters ")
            return 1
        if self.variateHalo.get() and ((float(self.haloFirstlowerValue.get()) > float(self.haloFirstupperValue.get()))
                                       or (float(self.haloFirstlowerValue.get())<=0)
                                       or (float(self.haloSecondlowerValue.get()) > float(self.haloSecondupperValue.get()))
                                       or (float(self.haloSecondlowerValue.get())<=0)):
            self.runLabelValue.set(" Error in halo parameters ")
            return 1
        fitParams = {}
        fitParams["bulgeVariate"] = self.variateBulge.get()
        fitParams["bulgeMLlower"] = float(self.bulgeMLlowerValue.get())
        fitParams["bulgeMLupper"] = float(self.bulgeMLupperValue.get())
        fitParams["diskVariate"] = self.variateDisk.get()
        fitParams["diskMLlower"] = float(self.diskMLlowerValue.get())
        fitParams["diskMLupper"] = float(self.diskMLupperValue.get())
        fitParams["haloVariate"] = self.variateHalo.get()
        fitParams["haloFirstlower"] = float(self.haloFirstlowerValue.get())
        fitParams["haloFirstupper"] = float(self.haloFirstupperValue.get())
        fitParams["haloSecondlower"] = float(self.haloSecondlowerValue.get())
        fitParams["haloSecondupper"] = float(self.haloSecondupperValue.get())
        t1 = time.time()
        self.mapButton.config(state="disabled")
        self.runLabelValue.set("         In process...         ")
        self.chi_map = self.rotCurve.fitBruteForce(fitParams)
        self.runLabelValue.set("       Done in %1.2f sec      " % (time.time()-t1))
        self.saveButton.config(state="normal")
        if self.variateDisk.get() and self.variateBulge.get():
            self.mapButton.config(state="normal")

    def save_fitted(self):
        self.bulgeMLratioValue.set(str(self.rotCurve.fittedBulgeML))
        self.diskMLratioValue.set(str(self.rotCurve.fittedDiskML))
        self.haloFirstParamValue.set(str(self.rotCurve.fittedHaloFirst))
        self.haloSecondParamValue.set(str(self.rotCurve.fittedHaloSecond))

    def show_map(self):
        x = arange(float(self.bulgeMLlowerValue.get()), float(self.bulgeMLupperValue.get())+0.01, 0.1)
        y = arange(float(self.diskMLlowerValue.get()), float(self.diskMLupperValue.get())+0.01, 0.1)
        X, Y = meshgrid(x, y)
        pcolor(X, Y, self.chi_map)
        xlabel("Bulge M/L")
        ylabel("Disk M/L")
        colorbar()
        plot([self.rotCurve.fittedBulgeML+0.05], [self.rotCurve.fittedDiskML+0.05], "ro")
        show()


class ConstantMLWindow(object):
    def __init__(self,
                 master,
                 rotCurve,
                 includeHalo,
                 bulgeMLratioValue,
                 diskMLratioValue,
                 haloFirstParamValue,
                 haloSecondParamValue):
        self.bulgeMLratioValue = bulgeMLratioValue
        self.diskMLratioValue = diskMLratioValue
        self.haloFirstParamValue = haloFirstParamValue
        self.haloSecondParamValue = haloSecondParamValue
        self.rotCurve = rotCurve
        self.bruteForceFrame = Tk.Toplevel(takefocus=True)
        self.bruteForceFrame.wm_attributes("-topmost", 1)
        self.bruteForceFrame.grab_set()
        xScreenSize = master.winfo_screenwidth()
        yScreenSize = master.winfo_screenheight()
        self.bruteForceFrame.geometry("+%i+%i" % (xScreenSize/2-250, yScreenSize/2-100))
        Tk.Label(self.bruteForceFrame, text="Chose models and ranges to variate:").grid(column=0, row=0, columnspan=5)
        self.haloState = "normal" if includeHalo else "disabled"

        # Bulge parameters
        Tk.Label(self.bruteForceFrame, text="Bulge and disk M-to-L  from").grid(column=0, row=1, columnspan=2)
        self.bothMLlowerValue = Tk.StringVar()
        self.bothMLlowerValue.set(self.rotCurve.bParams["MLratio"])
        self.bothMLlowerEntry = Tk.Spinbox(self.bruteForceFrame,
                                            textvariable=self.bothMLlowerValue, 
                                            width=5, 
                                            bg="white",
                                            from_=0.0,
                                            to=100,
                                            increment=0.1)
        self.bothMLlowerEntry.grid(column=2, row=1)
        self.bothMLlowerEntry.bind("<Button-4>", mouse_wheel_up)
        self.bothMLlowerEntry.bind("<Button-5>", mouse_wheel_down)
        Tk.Label(self.bruteForceFrame, text=" to ").grid(column=3, row=1)
        self.bothMLupperValue = Tk.StringVar()
        self.bothMLupperValue.set(self.rotCurve.bParams["MLratio"])
        self.bothMLupperEntry = Tk.Spinbox(self.bruteForceFrame,
                                            textvariable=self.bothMLupperValue,
                                            width=5,
                                            bg="white",
                                            from_=0.0,
                                            to=100,
                                            increment=0.1)
        self.bothMLupperEntry.grid(column=4, row=1)
        self.bothMLupperEntry.bind("<Button-4>", mouse_wheel_up)
        self.bothMLupperEntry.bind("<Button-5>", mouse_wheel_down)

        # Halo
        self.variateHalo = Tk.IntVar()
        self.variateHaloCButton = Tk.Checkbutton(self.bruteForceFrame, variable=self.variateHalo, text=" Halo: ", state=self.haloState)
        self.variateHaloCButton.grid(column=0, row=3, rowspan=2)

        if self.rotCurve.hParams["model"] == "isoterm":
            Tk.Label(self.bruteForceFrame, text="Rc  from").grid(column=1, row=3)
        elif self.rotCurve.hParams["model"] == "NFW":
            Tk.Label(self.bruteForceFrame, text="C  from").grid(column=1, row=3)
        self.haloFirstlowerValue = Tk.StringVar()
        self.haloFirstlowerValue.set(self.rotCurve.hParams["firstParam"])
        self.haloFirstlowerEntry = Tk.Spinbox(self.bruteForceFrame,
                                              textvariable=self.haloFirstlowerValue,
                                              width=5,
                                              bg="white",
                                              from_=0.0,
                                              to=100,
                                              increment=0.1,
                                              state=self.haloState)
        self.haloFirstlowerEntry.grid(column=2, row=3)
        if self.haloState == "normal":
            self.haloFirstlowerEntry.bind("<Button-4>", mouse_wheel_up)
            self.haloFirstlowerEntry.bind("<Button-5>", mouse_wheel_down)
        Tk.Label(self.bruteForceFrame, text=" to ").grid(column=3, row=3)
        self.haloFirstupperValue = Tk.StringVar()
        self.haloFirstupperValue.set(self.rotCurve.hParams["firstParam"])
        self.haloFirstupperEntry = Tk.Spinbox(self.bruteForceFrame,
                                              textvariable=self.haloFirstupperValue,
                                              width=5, 
                                              bg="white", 
                                              from_=0.0,
                                              to=100,
                                              increment=0.1,
                                              state=self.haloState)
        self.haloFirstupperEntry.grid(column=4, row=3)
        if self.haloState == "normal":
            self.haloFirstupperEntry.bind("<Button-4>", mouse_wheel_up)
            self.haloFirstupperEntry.bind("<Button-5>", mouse_wheel_down)

        if self.rotCurve.hParams["model"] == "isoterm":
            Tk.Label(self.bruteForceFrame, text="V(inf)  from").grid(column=1, row=4)
        elif self.rotCurve.hParams["model"] == "NFW":
            Tk.Label(self.bruteForceFrame, text="V200  from").grid(column=1, row=4)
        self.haloSecondlowerValue = Tk.StringVar()
        self.haloSecondlowerValue.set(self.rotCurve.hParams["secondParam"])
        self.haloSecondlowerEntry = Tk.Spinbox(self.bruteForceFrame,
                                               textvariable=self.haloSecondlowerValue,
                                               width=5,
                                               bg="white",
                                               from_=0.0,
                                               to=1000,
                                               increment=1.0,
                                               state=self.haloState)
        self.haloSecondlowerEntry.grid(column=2, row=4)
        if self.haloState == "normal":
            self.haloSecondlowerEntry.bind("<Button-4>", mouse_wheel_up)
            self.haloSecondlowerEntry.bind("<Button-5>", mouse_wheel_down)
        Tk.Label(self.bruteForceFrame, text=" to ").grid(column=3, row=4)
        self.haloSecondupperValue = Tk.StringVar()
        self.haloSecondupperValue.set(self.rotCurve.hParams["secondParam"])
        self.haloSecondupperEntry = Tk.Spinbox(self.bruteForceFrame,
                                               textvariable=self.haloSecondupperValue,
                                               width=5, 
                                               bg="white", 
                                               from_=0.0,
                                               to=1000,
                                               increment=1.0,
                                               state=self.haloState)
        self.haloSecondupperEntry.grid(column=4, row=4)
        if self.haloState == "normal":
            self.haloSecondupperEntry.bind("<Button-4>", mouse_wheel_up)
            self.haloSecondupperEntry.bind("<Button-5>", mouse_wheel_down)

        # Buttons
        self.runButton = Tk.Button(self.bruteForceFrame, text="Run", state="normal", command=self.run)
        self.runButton.grid(column=0, row=6)
        self.saveButton = Tk.Button(self.bruteForceFrame, text="Save", state="disabled", command=self.save_fitted)
        self.saveButton.grid(column=1, row=6)
        self.cancelButton = Tk.Button(self.bruteForceFrame,
                                      text="Close",
                                      state="normal",
                                      command=lambda: self.bruteForceFrame.destroy())
        self.cancelButton.grid(column=4, row=6)
        self.runLabelValue = Tk.StringVar()
        Tk.Label(self.bruteForceFrame, textvariable=self.runLabelValue).grid(column=1, row=5, columnspan=3)

    def run(self):
        if ((float(self.bothMLlowerValue.get()) > float(self.bothMLupperValue.get()))
            or (float(self.bothMLlowerValue.get())<=0)):
            self.runLabelValue.set("Error in M/L parameters")
            return 1
        if self.variateHalo.get() and ((float(self.haloFirstlowerValue.get()) > float(self.haloFirstupperValue.get()))
                                       or (float(self.haloFirstlowerValue.get())<=0)
                                       or (float(self.haloSecondlowerValue.get()) > float(self.haloSecondupperValue.get()))
                                       or (float(self.haloSecondlowerValue.get())<=0)):
            self.runLabelValue.set(" Error in halo parameters ")
            return 1
        fitParams = {}
        fitParams["bothMLlower"] = float(self.bothMLlowerValue.get())
        fitParams["bothMLupper"] = float(self.bothMLupperValue.get())
        fitParams["haloVariate"] = self.variateHalo.get()
        fitParams["haloFirstlower"] = float(self.haloFirstlowerValue.get())
        fitParams["haloFirstupper"] = float(self.haloFirstupperValue.get())
        fitParams["haloSecondlower"] = float(self.haloSecondlowerValue.get())
        fitParams["haloSecondupper"] = float(self.haloSecondupperValue.get())
        t1 = time.time()
        self.runLabelValue.set("         In process...         ")
        self.rotCurve.fitConstantML(fitParams)
        self.runLabelValue.set("       Done in %1.2f sec      " % (time.time()-t1))
        self.saveButton.config(state="normal")

    def save_fitted(self):
        self.bulgeMLratioValue.set(str(self.rotCurve.fittedBulgeML))
        self.diskMLratioValue.set(str(self.rotCurve.fittedDiskML))
        self.haloFirstParamValue.set(str(self.rotCurve.fittedHaloFirst))
        self.haloSecondParamValue.set(str(self.rotCurve.fittedHaloSecond))
        

class MaximalDiskWindow(object):
    def __init__(self,
                 master,
                 rotCurve,
                 includeBulge,
                 includeDisk,
                 includeHalo,
                 bulgeMLratioValue,
                 diskMLratioValue,
                 haloFirstParamValue,
                 haloSecondParamValue):
        self.bulgeMLratioValue = bulgeMLratioValue
        self.diskMLratioValue = diskMLratioValue
        self.haloFirstParamValue = haloFirstParamValue
        self.haloSecondParamValue = haloSecondParamValue
        self.rotCurve = rotCurve
        self.maximalDiskFrame = Tk.Toplevel(takefocus=True)
        self.maximalDiskFrame.wm_attributes("-topmost", 1)
        self.maximalDiskFrame.grab_set()
        xScreenSize = master.winfo_screenwidth()
        yScreenSize = master.winfo_screenheight()
        self.maximalDiskFrame.geometry("+%i+%i" % (xScreenSize/2-250, yScreenSize/2-100))
        Tk.Label(self.maximalDiskFrame, text="Chose models and ranges to variate:").grid(column=0, row=0, columnspan=5)
        self.bulgeState = "normal" if includeBulge else "disabled"
        self.diskState = "normal" if includeDisk else "disabled"
        self.haloState = "normal" if includeHalo else "disabled"

        # Bulge parameters
        self.variateBulge = Tk.IntVar()
        self.variateBulgeCButton = Tk.Checkbutton(self.maximalDiskFrame, variable=self.variateBulge, text="Bulge:", state=self.bulgeState)
        self.variateBulgeCButton.grid(column=0, row=1)
        Tk.Label(self.maximalDiskFrame, text="M-to-L  from").grid(column=1, row=1)
        self.bulgeMLlowerValue = Tk.StringVar()
        self.bulgeMLlowerValue.set(self.rotCurve.bParams["MLratio"])
        self.bulgeMLlowerEntry = Tk.Spinbox(self.maximalDiskFrame,
                                            textvariable=self.bulgeMLlowerValue, 
                                            width=5, 
                                            bg="white",
                                            from_=0.0,
                                            to=100,
                                            increment=0.1,
                                            state=self.bulgeState)
        self.bulgeMLlowerEntry.grid(column=2, row=1)
        if self.diskState == "normal":
            self.bulgeMLlowerEntry.bind("<Button-4>", mouse_wheel_up)
            self.bulgeMLlowerEntry.bind("<Button-5>", mouse_wheel_down)
        Tk.Label(self.maximalDiskFrame, text=" to ").grid(column=3, row=1)
        self.bulgeMLupperValue = Tk.StringVar()
        self.bulgeMLupperValue.set(self.rotCurve.bParams["MLratio"])
        self.bulgeMLupperEntry = Tk.Spinbox(self.maximalDiskFrame,
                                            textvariable=self.bulgeMLupperValue,
                                            width=5,
                                            bg="white",
                                            from_=0.0,
                                            to=100,
                                            increment=0.1, 
                                            state=self.bulgeState)
        self.bulgeMLupperEntry.grid(column=4, row=1)
        if self.bulgeState == "normal":
            self.bulgeMLupperEntry.bind("<Button-4>", mouse_wheel_up)
            self.bulgeMLupperEntry.bind("<Button-5>", mouse_wheel_down)

        # Disk parameters
        self.variateDisk = Tk.IntVar()
        self.variateDisk.set(1)
        self.variateDiskCButton = Tk.Checkbutton(self.maximalDiskFrame, variable=self.variateDisk, text=" Disk: ", state="disabled")
        self.variateDiskCButton.grid(column=0, row=2)

        Tk.Label(self.maximalDiskFrame, text="M-to-L  from").grid(column=1, row=2)
        self.diskMLlowerValue = Tk.StringVar()
        self.diskMLlowerValue.set(self.rotCurve.dParams["MLratio"])
        self.diskMLlowerEntry = Tk.Spinbox(self.maximalDiskFrame,
                                           textvariable=self.diskMLlowerValue,
                                           width=5,
                                           bg="white",
                                           from_=0.0,
                                           to=100,
                                           increment=0.1, 
                                           state=self.diskState)
        self.diskMLlowerEntry.grid(column=2, row=2)
        if self.diskState == "normal":
            self.diskMLlowerEntry.bind("<Button-4>", mouse_wheel_up)
            self.diskMLlowerEntry.bind("<Button-5>", mouse_wheel_down)
        Tk.Label(self.maximalDiskFrame, text=" to ").grid(column=3, row=2)
        self.diskMLupperValue = Tk.StringVar()
        self.diskMLupperValue.set(self.rotCurve.dParams["MLratio"])
        self.diskMLupperEntry = Tk.Spinbox(self.maximalDiskFrame,
                                           textvariable=self.diskMLupperValue,
                                           width=5, 
                                           bg="white", 
                                           from_=0.0,
                                           to=100,
                                           increment=0.1,
                                           state=self.diskState)
        self.diskMLupperEntry.grid(column=4, row=2)
        if self.diskState == "normal":
            self.diskMLupperEntry.bind("<Button-4>", mouse_wheel_up)
            self.diskMLupperEntry.bind("<Button-5>", mouse_wheel_down)

        # Halo
        self.variateHalo = Tk.IntVar()
        self.variateHaloCButton = Tk.Checkbutton(self.maximalDiskFrame, variable=self.variateHalo, text=" Halo: ", state=self.haloState)
        self.variateHaloCButton.grid(column=0, row=3, rowspan=2)

        if self.rotCurve.hParams["model"] == "isoterm":
            Tk.Label(self.maximalDiskFrame, text="Rc  from").grid(column=1, row=3)
        elif self.rotCurve.hParams["model"] == "NFW":
            Tk.Label(self.maximalDiskFrame, text="C  from").grid(column=1, row=3)
        self.haloFirstlowerValue = Tk.StringVar()
        self.haloFirstlowerValue.set(self.rotCurve.hParams["firstParam"])
        self.haloFirstlowerEntry = Tk.Spinbox(self.maximalDiskFrame,
                                              textvariable=self.haloFirstlowerValue,
                                              width=5,
                                              bg="white",
                                              from_=0.0,
                                              to=100,
                                              increment=0.1,
                                              state=self.haloState)
        self.haloFirstlowerEntry.grid(column=2, row=3)
        if self.haloState == "normal":
            self.haloFirstlowerEntry.bind("<Button-4>", mouse_wheel_up)
            self.haloFirstlowerEntry.bind("<Button-5>", mouse_wheel_down)
        Tk.Label(self.maximalDiskFrame, text=" to ").grid(column=3, row=3)
        self.haloFirstupperValue = Tk.StringVar()
        self.haloFirstupperValue.set(self.rotCurve.hParams["firstParam"])
        self.haloFirstupperEntry = Tk.Spinbox(self.maximalDiskFrame,
                                              textvariable=self.haloFirstupperValue,
                                              width=5, 
                                              bg="white", 
                                              from_=0.0,
                                              to=100,
                                              increment=0.1,
                                              state=self.haloState)
        self.haloFirstupperEntry.grid(column=4, row=3)
        if self.haloState == "normal":
            self.haloFirstupperEntry.bind("<Button-4>", mouse_wheel_up)
            self.haloFirstupperEntry.bind("<Button-5>", mouse_wheel_down)

        if self.rotCurve.hParams["model"] == "isoterm":
            Tk.Label(self.maximalDiskFrame, text="V(inf)  from").grid(column=1, row=4)
        elif self.rotCurve.hParams["model"] == "NFW":
            Tk.Label(self.maximalDiskFrame, text="V200  from").grid(column=1, row=4)
        self.haloSecondlowerValue = Tk.StringVar()
        self.haloSecondlowerValue.set(self.rotCurve.hParams["secondParam"])
        self.haloSecondlowerEntry = Tk.Spinbox(self.maximalDiskFrame,
                                               textvariable=self.haloSecondlowerValue,
                                               width=5,
                                               bg="white",
                                               from_=0.0,
                                               to=1000,
                                               increment=1.0,
                                               state=self.haloState)
        self.haloSecondlowerEntry.grid(column=2, row=4)
        if self.haloState == "normal":
            self.haloSecondlowerEntry.bind("<Button-4>", mouse_wheel_up)
            self.haloSecondlowerEntry.bind("<Button-5>", mouse_wheel_down)
        Tk.Label(self.maximalDiskFrame, text=" to ").grid(column=3, row=4)
        self.haloSecondupperValue = Tk.StringVar()
        self.haloSecondupperValue.set(self.rotCurve.hParams["secondParam"])
        self.haloSecondupperEntry = Tk.Spinbox(self.maximalDiskFrame,
                                               textvariable=self.haloSecondupperValue,
                                               width=5, 
                                               bg="white", 
                                               from_=0.0,
                                               to=1000,
                                               increment=1.0,
                                               state=self.haloState)
        self.haloSecondupperEntry.grid(column=4, row=4)
        if self.haloState == "normal":
            self.haloSecondupperEntry.bind("<Button-4>", mouse_wheel_up)
            self.haloSecondupperEntry.bind("<Button-5>", mouse_wheel_down)

        # Buttons
        self.runButton = Tk.Button(self.maximalDiskFrame, text="Run", state="normal", command=self.run)
        self.runButton.grid(column=0, row=6)
        self.saveButton = Tk.Button(self.maximalDiskFrame, text="Save", state="disabled", command=self.save_fitted)
        self.saveButton.grid(column=1, row=6)
        self.cancelButton = Tk.Button(self.maximalDiskFrame,
                                      text="Close",
                                      state="normal",
                                      command=lambda: self.maximalDiskFrame.destroy())
        self.cancelButton.grid(column=3, row=6)
        self.runLabelValue = Tk.StringVar()
        Tk.Label(self.maximalDiskFrame, textvariable=self.runLabelValue).grid(column=1, row=5, columnspan=3)

        # Slider
        self.diskMLSliderValue = Tk.DoubleVar()
        self.diskMLSlider = Tk.Scale(self.maximalDiskFrame,
                                     from_=float(self.diskMLlowerValue.get()),
                                     to=float(self.diskMLupperValue.get()),
                                     orient=Tk.HORIZONTAL,
                                     resolution=0.1,
                                     length=180,
                                     variable=self.diskMLSliderValue)
        self.diskMLSliderValue.trace("w",
                                     lambda n, i, m, v=self.diskMLSliderValue: self.sliderMoved(v.get()))
        self.diskMLSlider.grid(column=1, row=7, columnspan=3)
        self.diskMLSliderLeftValue = Tk.StringVar()
        self.diskMLSliderRightValue = Tk.StringVar()
        Tk.Label(self.maximalDiskFrame, textvariable=self.diskMLSliderLeftValue).grid(column=0, row=7)
        Tk.Label(self.maximalDiskFrame, textvariable=self.diskMLSliderRightValue).grid(column=4, row=7)

        # Image
        self.imgLabel = Tk.Label(self.maximalDiskFrame)
        self.imgLabel.grid(column=5, row=0, rowspan=8)

        # The text under the slider
        Tk.Label(self.maximalDiskFrame, text="Bulge M/L").grid(column=0, row=8)
        self.selectedBulgeML = Tk.StringVar()
        Tk.Label(self.maximalDiskFrame, textvariable=self.selectedBulgeML).grid(column=1, row=8)
        if self.rotCurve.hParams["model"] == "isoterm":
            Tk.Label(self.maximalDiskFrame, text="Halo Rc").grid(column=0, row=9)
            Tk.Label(self.maximalDiskFrame, text="Halo V(inf)").grid(column=0, row=10)
        elif self.rotCurve.hParams["model"] == "NFW":
            Tk.Label(self.maximalDiskFrame, text="Halo C").grid(column=0, row=9)
            Tk.Label(self.maximalDiskFrame, text="Halo V200").grid(column=0, row=10)
        self.selectedHaloFirst = Tk.StringVar()
        Tk.Label(self.maximalDiskFrame, textvariable=self.selectedHaloFirst).grid(column=1, row=9)
        self.selectedHaloSecond = Tk.StringVar()
        Tk.Label(self.maximalDiskFrame, textvariable=self.selectedHaloSecond).grid(column=1, row=10)
        # Labels for "near to the edge" cautions
        self.bulgeMLCautionLabel = Tk.Label(self.maximalDiskFrame)    # Bulge
        self.bulgeMLCautionLabel.grid(column=2, row=8, columnspan=2)  #
        self.haloFirstCautionLabel = Tk.Label(self.maximalDiskFrame)
        self.haloFirstCautionLabel.grid(column=2, row=9, columnspan=2)
        self.haloSecondCautionLabel = Tk.Label(self.maximalDiskFrame)
        self.haloSecondCautionLabel.grid(column=2, row=10, columnspan=2)
        

    def sliderMoved(self, value):
        index = int((value - float(self.diskMLlowerValue.get())) / 0.1)
        diskMLopt = value
        bulgeMLopt, haloFirstOpt, haloSecondOpt = self.bhOptimalList[index]
        self.imgLabel.config(image=self.plotList[index])
        self.selectedBulgeML.set(str(bulgeMLopt))
        self.selectedHaloFirst.set(str(haloFirstOpt))
        self.selectedHaloSecond.set(str(haloSecondOpt))
        # if optimal value of some parameter is too near to the edge of a
        # searching area then corresponding message is written
        if (bulgeMLopt - 0.05 < float(self.bulgeMLlowerValue.get())) or (bulgeMLopt + 0.05 > float(self.bulgeMLupperValue.get())):
            self.bulgeMLCautionLabel.config(text="<-near the edge", foreground="red")
        else:
            self.bulgeMLCautionLabel.config(text="", foreground="red")
        if (haloFirstOpt - 0.05 < float(self.haloFirstlowerValue.get())) or (haloFirstOpt + 0.05 > float(self.haloFirstupperValue.get())):
            self.haloFirstCautionLabel.config(text="<-near the edge", foreground="red")
        else:
            self.haloFirstCautionLabel.config(text="", foreground="red")
        if (haloSecondOpt - 0.05 < float(self.haloSecondlowerValue.get())) or (haloSecondOpt + 0.05 > float(self.haloSecondupperValue.get())):
            self.haloSecondCautionLabel.config(text="<-near the edge", foreground="red")
        else:
            self.haloSecondCautionLabel.config(text="", foreground="red")



    def run(self):
        if self.variateBulge.get() and ((float(self.bulgeMLlowerValue.get()) > float(self.bulgeMLupperValue.get()))
                                        or (float(self.bulgeMLlowerValue.get())<=0)):
            self.runLabelValue.set("Error in bulge parameters")
            return 1
        if self.variateDisk.get() and ((float(self.diskMLlowerValue.get()) > float(self.diskMLupperValue.get()))
                                        or (float(self.diskMLlowerValue.get())<=0)):
            self.runLabelValue.set(" Error in disk parameters ")
            return 1
        if self.variateHalo.get() and ((float(self.haloFirstlowerValue.get()) > float(self.haloFirstupperValue.get()))
                                       or (float(self.haloFirstlowerValue.get())<=0)
                                       or (float(self.haloSecondlowerValue.get()) > float(self.haloSecondupperValue.get()))
                                       or (float(self.haloSecondlowerValue.get())<=0)):
            self.runLabelValue.set(" Error in halo parameters ")
            return 1
        fitParams = {}
        fitParams["bulgeVariate"] = self.variateBulge.get()
        fitParams["bulgeMLlower"] = float(self.bulgeMLlowerValue.get())
        fitParams["bulgeMLupper"] = float(self.bulgeMLupperValue.get())
        fitParams["diskVariate"] = self.variateDisk.get()
        fitParams["diskMLlower"] = float(self.diskMLlowerValue.get())
        fitParams["diskMLupper"] = float(self.diskMLupperValue.get())
        fitParams["haloVariate"] = self.variateHalo.get()
        fitParams["haloFirstlower"] = float(self.haloFirstlowerValue.get())
        fitParams["haloFirstupper"] = float(self.haloFirstupperValue.get())
        fitParams["haloSecondlower"] = float(self.haloSecondlowerValue.get())
        fitParams["haloSecondupper"] = float(self.haloSecondupperValue.get())
        t1 = time.time()
        self.runLabelValue.set("         In process...         ")
        self.bhOptimalList, self.plotList = self.rotCurve.fitMaximalDisk(fitParams)
        self.runLabelValue.set("       Done in %1.2f sec      " % (time.time()-t1))
        self.saveButton.config(state="normal")
        self.diskMLSlider.config(state="normal",
                                 from_=float(self.diskMLlowerValue.get()),
                                 to=float(self.diskMLupperValue.get()))
        self.diskMLSliderLeftValue.set(self.diskMLlowerValue.get())
        self.diskMLSliderRightValue.set(self.diskMLupperValue.get())
        self.diskMLSliderValue.set(self.diskMLlowerValue.get())

    def save_fitted(self):
        value = self.diskMLSliderValue.get()
        index = int((value - float(self.diskMLlowerValue.get())) / 0.1)
        diskMLopt = value
        bulgeMLopt, haloFirstOpt, haloSecondOpt = self.bhOptimalList[index]
        self.bulgeMLratioValue.set(str(bulgeMLopt))
        self.diskMLratioValue.set(str(diskMLopt))
        self.haloFirstParamValue.set(str(haloFirstOpt))
        self.haloSecondParamValue.set(str(haloSecondOpt))


class optimalFitWindow(object):
    """ Fitting by gradient descent method (scipy.optimize.fmin function) """
    def __init__(self,
                 master,
                 rotCurve,
                 bulgeMLratioValue,
                 diskMLratioValue,
                 haloFirstParamValue,
                 haloSecondParamValue):
        self.bulgeMLratioValue = bulgeMLratioValue
        self.diskMLratioValue = diskMLratioValue
        self.haloFirstParamValue = haloFirstParamValue
        self.haloSecondParamValue = haloSecondParamValue
        self.rotCurve = rotCurve
        self.optimalFitFrame = Tk.Toplevel(takefocus=True)
        self.optimalFitFrame.wm_attributes("-topmost", 1)
        self.optimalFitFrame.grab_set()
        xScreenSize = master.winfo_screenwidth()
        yScreenSize = master.winfo_screenheight()
        self.optimalFitFrame.geometry("+%i+%i" % (xScreenSize/2-250, yScreenSize/2-100))
        Tk.Label(self.optimalFitFrame, text="Gradient descent running... ").grid(column=0, row=0, columnspan=2)
        # Two buttons: save results of fitting and close window without saving 
        self.saveButton = Tk.Button(self.optimalFitFrame, text="Save", state="normal", command=self.save_fitted)       
        self.saveButton.grid(column=0, row=6)
        self.cancelButton = Tk.Button(self.optimalFitFrame,
                                      text="Close",
                                      state="normal",
                                      command=lambda: self.optimalFitFrame.destroy())
        self.cancelButton.grid(column=2, row=6)
        # Running of the gradient descent optimization
        self.MLbulgeOpt, self.MLdiskOpt, self.haloFirstOpt, self.haloSecondOpt = self.rotCurve.fitOptimal()
        # Show results in the small window
        Tk.Label(self.optimalFitFrame, text="Done").grid(column=2, row=0)
        Tk.Label(self.optimalFitFrame, text="Optimal values").grid(column=0, row=1)
        Tk.Label(self.optimalFitFrame, text="Bulge M/L = %1.1f" % (self.MLbulgeOpt)).grid(column=0, row=2)
        Tk.Label(self.optimalFitFrame, text="Disk M/L = %1.1f" % (self.MLdiskOpt)).grid(column=0, row=3)
        if self.rotCurve.hParams["model"] == "isoterm":
            Tk.Label(self.optimalFitFrame, text="Rc = %1.1f" % (self.haloFirstOpt)).grid(column=0, row=4)
            Tk.Label(self.optimalFitFrame, text="V(inf) = %1.1f" % (self.haloSecondOpt)).grid(column=0, row=5)
        elif self.rotCurve.hParams["model"] == "NFW":
            Tk.Label(self.optimalFitFrame, text="C = %1.1f" % (self.haloFirstOpt)).grid(column=0, row=4)
            Tk.Label(self.optimalFitFrame, text="V200 = %1.1f" % (self.haloSecondOpt)).grid(column=0, row=5)

    def save_fitted(self):
        self.bulgeMLratioValue.set("%1.1f"%(self.MLbulgeOpt))
        self.diskMLratioValue.set("%1.1f"%(self.MLdiskOpt))
        self.haloFirstParamValue.set("%1.1f"%(self.haloFirstOpt))
        self.haloSecondParamValue.set("%1.1f"%(self.haloSecondOpt))
        self.optimalFitFrame.destroy()


class MaximalDiskOptWindow(object):
    def __init__(self,
                 master,
                 rotCurve,
                 bulgeMLratioValue,
                 diskMLratioValue,
                 haloFirstParamValue,
                 haloSecondParamValue):
        self.bulgeMLratioValue = bulgeMLratioValue
        self.diskMLratioValue = diskMLratioValue
        self.haloFirstParamValue = haloFirstParamValue
        self.haloSecondParamValue = haloSecondParamValue
        self.rotCurve = rotCurve
        self.maximalDiskFrame = Tk.Toplevel(takefocus=True)
        self.maximalDiskFrame.wm_attributes("-topmost", 1)
        self.maximalDiskFrame.grab_set()
        xScreenSize = master.winfo_screenwidth()
        yScreenSize = master.winfo_screenheight()
        self.maximalDiskFrame.geometry("+%i+%i" % (xScreenSize/2-250, yScreenSize/2-100))
        Tk.Label(self.maximalDiskFrame, text="Chose models and ranges to variate:").grid(column=0, row=0, columnspan=5)

        # Disk parameters
        Tk.Label(self.maximalDiskFrame, text="M-to-L  from").grid(column=1, row=2)
        self.diskMLlowerValue = Tk.StringVar()
        self.diskMLlowerValue.set(self.rotCurve.dParams["MLratio"])
        self.diskMLlowerEntry = Tk.Spinbox(self.maximalDiskFrame,
                                           textvariable=self.diskMLlowerValue,
                                           width=5,
                                           bg="white",
                                           from_=0.0,
                                           to=100,
                                           increment=0.1)
        self.diskMLlowerEntry.grid(column=2, row=2)
        self.diskMLlowerEntry.bind("<Button-4>", mouse_wheel_up)
        self.diskMLlowerEntry.bind("<Button-5>", mouse_wheel_down)
        Tk.Label(self.maximalDiskFrame, text=" to ").grid(column=3, row=2)
        self.diskMLupperValue = Tk.StringVar()
        self.diskMLupperValue.set(self.rotCurve.dParams["MLratio"])
        self.diskMLupperEntry = Tk.Spinbox(self.maximalDiskFrame,
                                           textvariable=self.diskMLupperValue,
                                           width=5, 
                                           bg="white", 
                                           from_=0.0,
                                           to=100,
                                           increment=0.1)
        self.diskMLupperEntry.grid(column=4, row=2)
        self.diskMLupperEntry.bind("<Button-4>", mouse_wheel_up)
        self.diskMLupperEntry.bind("<Button-5>", mouse_wheel_down)

        # Buttons
        self.runButton = Tk.Button(self.maximalDiskFrame, text="Run", state="normal", command=self.run)
        self.runButton.grid(column=0, row=6)
        self.saveButton = Tk.Button(self.maximalDiskFrame, text="Save", state="disabled", command=self.save_fitted)
        self.saveButton.grid(column=1, row=6)
        self.cancelButton = Tk.Button(self.maximalDiskFrame,
                                      text="Close",
                                      state="normal",
                                      command=lambda: self.maximalDiskFrame.destroy())
        self.cancelButton.grid(column=3, row=6)
        self.runLabelValue = Tk.StringVar()
        Tk.Label(self.maximalDiskFrame, textvariable=self.runLabelValue).grid(column=1, row=5, columnspan=3)

        # Slider
        self.diskMLSliderValue = Tk.DoubleVar()
        self.diskMLSlider = Tk.Scale(self.maximalDiskFrame,
                                     from_=float(self.diskMLlowerValue.get()),
                                     to=float(self.diskMLupperValue.get()),
                                     orient=Tk.HORIZONTAL,
                                     resolution=0.1,
                                     length=180,
                                     variable=self.diskMLSliderValue)
        self.diskMLSliderValue.trace("w",
                                     lambda n, i, m, v=self.diskMLSliderValue: self.sliderMoved(v.get()))
        self.diskMLSlider.grid(column=1, row=7, columnspan=3)
        self.diskMLSliderLeftValue = Tk.StringVar()
        self.diskMLSliderRightValue = Tk.StringVar()
        Tk.Label(self.maximalDiskFrame, textvariable=self.diskMLSliderLeftValue).grid(column=0, row=7)
        Tk.Label(self.maximalDiskFrame, textvariable=self.diskMLSliderRightValue).grid(column=4, row=7)

        # Image
        self.imgLabel = Tk.Label(self.maximalDiskFrame)
        self.imgLabel.grid(column=5, row=0, rowspan=8)

        # The text under the slider
        Tk.Label(self.maximalDiskFrame, text="Bulge M/L").grid(column=0, row=8)
        self.selectedBulgeML = Tk.StringVar()
        Tk.Label(self.maximalDiskFrame, textvariable=self.selectedBulgeML).grid(column=1, row=8)
        if self.rotCurve.hParams["model"] == "isoterm":
            Tk.Label(self.maximalDiskFrame, text="Halo Rc").grid(column=0, row=9)
            Tk.Label(self.maximalDiskFrame, text="Halo V(inf)").grid(column=0, row=10)
        elif self.rotCurve.hParams["model"] == "NFW":
            Tk.Label(self.maximalDiskFrame, text="Halo C").grid(column=0, row=9)
            Tk.Label(self.maximalDiskFrame, text="Halo V200").grid(column=0, row=10)
        self.selectedHaloFirst = Tk.StringVar()
        Tk.Label(self.maximalDiskFrame, textvariable=self.selectedHaloFirst).grid(column=1, row=9)
        self.selectedHaloSecond = Tk.StringVar()
        Tk.Label(self.maximalDiskFrame, textvariable=self.selectedHaloSecond).grid(column=1, row=10)

    def sliderMoved(self, value):
        index = int((value - float(self.diskMLlowerValue.get())) / 0.1)
        diskMLopt = value
        bulgeMLopt, haloFirstOpt, haloSecondOpt = self.bhOptimalList[index]
        self.imgLabel.config(image=self.plotList[index])
        self.selectedBulgeML.set(str(bulgeMLopt))
        self.selectedHaloFirst.set(str(haloFirstOpt))
        self.selectedHaloSecond.set(str(haloSecondOpt))

    def run(self):
        if ((float(self.diskMLlowerValue.get()) > float(self.diskMLupperValue.get()))
                                        or (float(self.diskMLlowerValue.get())<=0)):
            self.runLabelValue.set(" Error in disk parameters ")
            return 1
        fitParams = {}
        fitParams["diskMLlower"] = float(self.diskMLlowerValue.get())
        fitParams["diskMLupper"] = float(self.diskMLupperValue.get())
        t1 = time.time()
        self.runLabelValue.set("         In process...         ")
        self.bhOptimalList, self.plotList = self.rotCurve.fitMaximalDisk2(fitParams)
        self.runLabelValue.set("       Done in %1.2f sec      " % (time.time()-t1))
        self.saveButton.config(state="normal")
        self.diskMLSlider.config(state="normal",
                                 from_=float(self.diskMLlowerValue.get()),
                                 to=float(self.diskMLupperValue.get()))
        self.diskMLSliderLeftValue.set(self.diskMLlowerValue.get())
        self.diskMLSliderRightValue.set(self.diskMLupperValue.get())
        self.diskMLSliderValue.set(self.diskMLlowerValue.get())

    def save_fitted(self):
        value = self.diskMLSliderValue.get()
        index = int((value - float(self.diskMLlowerValue.get())) / 0.1)
        diskMLopt = value
        bulgeMLopt, haloFirstOpt, haloSecondOpt = self.bhOptimalList[index]
        self.bulgeMLratioValue.set(str(bulgeMLopt))
        self.diskMLratioValue.set(str(diskMLopt))
        self.haloFirstParamValue.set(str(haloFirstOpt))
        self.haloSecondParamValue.set(str(haloSecondOpt))

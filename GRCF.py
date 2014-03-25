#! /usr/bin/env python

import pylab

import Tkinter as Tk
import tkFileDialog
import tkMessageBox
import tkFont

from Pmw import Balloon

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

from GRCFlibs.GRCFmathFunctions import *
from GRCFlibs.GRCFifaceFunctions import *

from math import acos, sqrt, degrees


def get_inclination():
    q = float(diskAxisRatioValue.get())
    q0 = float(diskThicknessValue.get())
    if q0 < q <1.0:
        return degrees(acos(sqrt((q**2 - q0**2) / (1-q0**2))))
    return 90.0

def loadVelocityData():
    fileName = tkFileDialog.askopenfilename(parent=master,
                                 filetypes=[("Data files", "*.dat"), ("All files", ".*")],
                                 title="Open data file")
    distance, velocity, sigma = getRotationCurve(fileName)
    global rotCurve 
    rotCurve = GalaxyRotation(distance, 
                              velocity, 
                              sigma, 
                              float(generalScaleValue.get()), 
                              mainGraph, 
                              canvas,
                              fileName)
    rotCurve.plot()
    correctForInclinationCB.config(state="normal")
    generalSunMagEntry.config(state="normal")
    generalLDEntry.config(state="normal")
    generalScaleEntry.config(state="normal")
    generalHubbleEntry.config(state="normal")
    includeDiskCButton.config(state="normal")
    includeBulgeCButton.config(state="normal")
    includeHaloCButton.config(state="normal")
    runButton.config(state="normal")
    fileMenu.entryconfig("Save parameters", state="normal")
    fileMenu.entryconfig("Load parameters", state="normal")
    fileMenu.entryconfig("Save velocity", state="normal")
    viewMenu.entryconfig("Show legend", state="normal")
    viewMenu.entryconfig("Coloured", state="normal")
    viewMenu.entryconfig("Chi squared", state="normal")

def getValuesFromAllFields():
    gParams = {}
    # If correction of the data for the inclination is ON
    # then the inclination is computed from q and z0/h values of the disc.
    # in other case inclination is just setted to -1 deg
    if correctForInclination.get() != 0:
        incl = get_inclination()
    else: 
        incl = -1.0
    gParams["incl"] = incl
    gParams["iCorrect"] = correctForInclination.get()
    # all other values just getted from corresponding fields
    gParams["LD"] = generalLDValue.get()
    gParams["scale"] = generalScaleValue.get()
    gParams["hubble"] = generalHubbleValue.get()
    gParams["Msun"] = generalSunMagValue.get()
    bParams = {}
    bParams["include"] = includeBulge.get()
    bParams["effSurfBri"] = bulgeEffSurfBriValue.get()
    bParams["sersicIndex"] = bulgeSersicIndexValue.get()
    bParams["effRadius"] = bulgeEffRadiusValue.get()
    bParams["axisRatio"] = bulgeAxisRatioValue.get()
    bParams["MLratio"] = bulgeMLratioValue.get()
    dParams = {}
    dParams["include"] = includeDisk.get()
    dParams["cenSurfBri"] = diskCenSurfBriValue.get()
    dParams["expScale"] = diskExpScaleValue.get()
    dParams["thickness"] = diskThicknessValue.get()
    dParams["MLratio"] = diskMLratioValue.get()
    dParams["axisRatio"] = diskAxisRatioValue.get()
    hParams = {}
    hParams["include"] = includeHalo.get()
    hParams["firstParam"] = haloFirstParamValue.get()
    hParams["secondParam"] = haloSecondParamValue.get()
    hParams["model"] = haloModelValue.get()
    hParams["includeAC"] = haloIncludeAC.get()
    return gParams, bParams, dParams, hParams


def setValuesToAllFields(params):
    if params[0] is None:
        return
    gParams = params[0]
    bParams = params[1]
    dParams = params[2]
    hParams = params[3]
    generalScaleValue.set(gParams["scale"])
    generalSunMagValue.set(gParams["Msun"])
    generalHubbleValue.set(gParams["hubble"])
    generalLDValue.set(gParams["LD"])
    correctForInclination.set(gParams["iCorrect"])
    includeBulge.set(bParams["include"])
    bulgeEffSurfBriValue.set(bParams["effSurfBri"])
    bulgeSersicIndexValue.set(bParams["sersicIndex"])
    bulgeEffRadiusValue.set(bParams["effRadius"])
    bulgeAxisRatioValue.set(bParams["axisRatio"])
    bulgeMLratioValue.set(bParams["MLratio"])
    includeDisk.set(dParams["include"])
    diskCenSurfBriValue.set(dParams["cenSurfBri"])
    diskExpScaleValue.set(dParams["expScale"])
    diskThicknessValue.set(dParams["thickness"])
    diskMLratioValue.set(dParams["MLratio"])
    diskAxisRatioValue.set(dParams["axisRatio"])
    includeHalo.set(hParams["include"])
    haloFirstParamValue.set(hParams["firstParam"])
    haloSecondParamValue.set(hParams["secondParam"])
    haloModelValue.set(hParams["model"])
    haloIncludeAC.set(hParams["includeAC"])

def runComputation():
    gParams, bParams, dParams, hParams = getValuesFromAllFields()
    # Are values of all parameters correct?
    resOfCheck, failParam, reasonOfResult = checAllValues(gParams, bParams, dParams, hParams)
    # If at least one parameter is incorrect, show popup window and stop computation
    if resOfCheck is False:
            tkMessageBox.showerror("Value error", "%s value is incorrect \n (%s)" % (failParam, reasonOfResult))
            return False
    # If all is Ok
    runButton.config(state="disabled")
    rotCurve.makeComputation(gParams, bParams, dParams, hParams)
    master.title("Galaxy Rotation Curve Fit")
    # Fitting has sence only after initial computation
    fitMenu.entryconfig("Best chi squared", state="normal")
    fitMenu.entryconfig("Gradient descent", state="normal")
    # Maximal disk approximation works only if the disk model is on
    if includeDisk.get() > 0:
        fitMenu.entryconfig("Maximal disk", state="normal")
        fitMenu.entryconfig("Maximal disk opt.", state="normal")
    # Constant M/L approximation works only if the disk and the bulge models are on
    if (includeBulge.get() > 0) and (includeDisk.get() > 0):
        fitMenu.entryconfig("Constant M/L", state="normal")
    runButton.config(state="normal")


def some_parameter_changed(parameter, newValue):
    """ This function calls every time when any parameter
    of galaxy, bulge, disk or halo is changes """
    if parameter == "viewLegend": 
        rotCurve.viewLegend = newValue
        rotCurve.plot()
        return 0
    if parameter == "colouredPaint":
        rotCurve.colouredPaint = newValue
        rotCurve.plot()
        return 0
    if parameter == "showChiSquared":
        rotCurve.showChiSquared = newValue
        rotCurve.plot()
        return 0
    master.title("Galaxy Rotation Curve Fit (*)")
    fitMenu.entryconfig("Best chi squared", state="disabled")   # fitting is not allowed when parameters are changed
    fitMenu.entryconfig("Constant M/L", state="disabled")       #
    fitMenu.entryconfig("Maximal disk", state="disabled")       #
    fitMenu.entryconfig("Maximal disk opt.", state="disabled")  #
    fitMenu.entryconfig("Gradient descent", state="disabled")   #
    rotCurve.parametersChanged = True
    #  If we include adiabatic contraction in halo model then
    #  changing of any parameter of the disc and bulge will
    #  affect halo shape and we have to recompute all halo model
    if haloIncludeAC.get() == 1:
        rotCurve.recomputeHalo = True
    # Hereafter is checking of disc and bulge parameters changing
    if ((parameter == "dThickness") or
        (parameter == "dAxisRatio") or
        (parameter == "inclCorrect")):
        if correctForInclination.get() == 0:
            rotCurve.deproject(-1.0)
        else:
            incl = get_inclination()
            rotCurve.deproject(incl)
    if parameter == "scale":
        rotCurve.reScale(newValue)
    if parameter == "bInclude":
        onoffPanel(bulgePanel, newValue)
    if parameter == "dInclude":
        onoffPanel(diskPanel, newValue)
    if parameter == "hInclude":
        onoffPanel(haloPanel, newValue)
        if newValue and (haloModelValue.get() == "NFW"):   # Adiabatic contraction only for NFW profile
            haloACCheckbutton.config(state="normal")
        else:
            haloACCheckbutton.config(state="disabled")
    if parameter == "haloModel":
        if newValue == "NFW":
            haloACCheckbutton.config(state="normal")
        else:
            haloACCheckbutton.config(state="disabled")
    if parameter == "Msun":
        for item, value in mSunBands.iteritems():
            if value == float(newValue):
                generalBandValue.set(item)
                return 0
        generalBandValue.set("---")

#    fitMenu.entryconfig("Best chi squared", state="normal")
#    master.title("Galaxy Rotation Curve Fit")

# Creating the main window
master = Tk.Tk()
font11 = tkFont.Font(size=11)
master.title("Galaxy Rotation Curve Fit")
master.geometry(("950x600"))

############################################################
#                Creating menu                             #
############################################################

menubar = Tk.Menu(master)
fileMenu = Tk.Menu(menubar, tearoff=0)
fileMenu.add_command(label="Load velocity", command=loadVelocityData)
fileMenu.add_command(label="Save parameters",
                     command=lambda: saveParams(master, getValuesFromAllFields()),
                     state="disabled")
fileMenu.add_command(label="Load parameters", 
                     command=lambda: setValuesToAllFields(loadParams(master)), 
                     state="disabled")
fileMenu.add_command(label="Save velocity",
                     command=lambda: saveVelocity(master, rotCurve),
                     state="disabled")
menubar.add_cascade(label="File", menu=fileMenu)

viewMenu = Tk.Menu(menubar, tearoff=0)
showLegend = Tk.IntVar()
showLegend.set(1)
viewMenu.add_checkbutton(label="Show legend", 
                         variable=showLegend, 
                         state="disabled")
showLegend.trace("w", lambda n, i, m, v=showLegend: some_parameter_changed("viewLegend", v.get()))
colouredPaint = Tk.IntVar()
colouredPaint.set(1)
viewMenu.add_checkbutton(label="Coloured",
                         variable=colouredPaint,
                         state="disabled")
colouredPaint.trace("w", lambda n, i, m, v=colouredPaint: some_parameter_changed("colouredPaint", v.get()))
showChiSquared = Tk.IntVar()
showChiSquared.set(1)
viewMenu.add_checkbutton(label="Chi squared",
                         variable=showChiSquared,
                         state="disabled")
showChiSquared.trace("w", lambda n, i, m, v=showChiSquared: some_parameter_changed("showChiSquared", v.get()))
menubar.add_cascade(label="View", menu=viewMenu)

fitMenu = Tk.Menu(menubar, tearoff=0)
fitMenu.add_command(label="Best chi squared",
                    command=lambda: BruteForceWindow(master,
                                                     rotCurve,
                                                     includeBulge.get(),
                                                     includeDisk.get(),
                                                     includeHalo.get(),
                                                     bulgeMLratioValue,
                                                     diskMLratioValue,
                                                     haloFirstParamValue,
                                                     haloSecondParamValue),
                    state="disabled")
fitMenu.add_command(label="Constant M/L",
                    command=lambda: ConstantMLWindow(master,
                                                     rotCurve,
                                                     includeHalo.get(),
                                                     bulgeMLratioValue,
                                                     diskMLratioValue,
                                                     haloFirstParamValue,
                                                     haloSecondParamValue),
                    state="disabled")

fitMenu.add_command(label="Maximal disk",
                    command=lambda: MaximalDiskWindow(master,
                                                     rotCurve,
                                                     includeBulge.get(),
                                                     includeDisk.get(),
                                                     includeHalo.get(),
                                                     bulgeMLratioValue,
                                                     diskMLratioValue,
                                                     haloFirstParamValue,
                                                     haloSecondParamValue),
                    state="disabled")

fitMenu.add_command(label="Maximal disk opt.",
                    command=lambda: MaximalDiskOptWindow(master,
                                                         rotCurve,
                                                         bulgeMLratioValue,
                                                         diskMLratioValue,
                                                         haloFirstParamValue,
                                                         haloSecondParamValue),
                    state="disabled")

fitMenu.add_command(label="Gradient descent",
                    command=lambda: optimalFitWindow(master,
                                                     rotCurve,
                                                     bulgeMLratioValue,
                                                     diskMLratioValue,
                                                     haloFirstParamValue,
                                                     haloSecondParamValue),
                    state="disabled")

menubar.add_cascade(label="Fit", menu=fitMenu)


menubar.add_command(label="Quit", command=master.quit)
master.config(menu=menubar)

############################################################
#                  End of menu                             #
############################################################



############################################################
#                  Creating right panel                    #
############################################################

rightPanel = Tk.Frame(master)
rightPanel.pack(side=Tk.RIGHT, expand=1)

##########################
#   general parameters   #
##########################

generalPanel = Tk.Frame(rightPanel)
generalBalloon = Balloon(generalPanel)
generalPanel.grid(column=0, row=1)

# Place checkbutton for correcting for inclination question
correctForInclination = Tk.IntVar()
correctForInclination.set(0)
correctForInclination.trace("w",lambda n, i, m, v=correctForInclination: some_parameter_changed("inclCorrect", v.get()))
correctForInclinationCB = Tk.Checkbutton(generalPanel,
                                         text="Correct for inclination?",
                                         variable=correctForInclination,
                                         state="disabled")

correctForInclinationText = """If this option is on, observed rotation curve will be corrected
for inclination computed from disc's q and z0/h."""
generalBalloon.bind(correctForInclinationCB, correctForInclinationText)
correctForInclinationCB.grid(column=0, row=0, columnspan=3)

# Luminosity distance entry
Tk.Label(generalPanel, text="    LD", width=6).grid(column=0, row=1, sticky=Tk.E)
generalLDValue = Tk.StringVar()
generalLDValue.set("10.00")
generalLDValue.trace("w", 
                        lambda n, i, m, v=generalLDValue: some_parameter_changed("LD", v.get()))
generalLDEntry = Tk.Entry(generalPanel, textvariable=generalLDValue, width=5, state="disabled", bg="white")
generalLDEntry.grid(column=1, row=1, sticky=Tk.W)
Tk.Label(generalPanel, text="Mpc        ", width=7).grid(column=2, row=1, sticky=Tk.W)
generalBalloon.bind(generalLDEntry, "Luminosity distance of the galaxy [Mpc].")

# Place entry for galaxy scale
Tk.Label(generalPanel, text=" scale", width=6).grid(column=0, row=2, sticky=Tk.E)
generalScaleValue = Tk.StringVar()
generalScaleValue.set("0.48")
generalScaleValue.trace("w", 
                        lambda n, i, m, v=generalScaleValue: some_parameter_changed("scale", v.get()))
generalScaleEntry = Tk.Entry(generalPanel, textvariable=generalScaleValue, width=5, state="disabled", bg="white")
generalScaleEntry.grid(column=1, row=2, sticky=Tk.W)
Tk.Label(generalPanel, text="kpc/''      ", width=7).grid(column=2, row=2, sticky=Tk.W)
generalBalloon.bind(generalScaleEntry, "Scale of the galaxy [kpc per arcsec].")

# Hubble parameter value
Tk.Label(generalPanel, text=u"     H\u2080", font=font11, width=6).grid(column=0, row=3, sticky=Tk.E)
generalHubbleValue = Tk.StringVar()
generalHubbleValue.set("67.0")
generalHubbleValue.trace("w", 
                        lambda n, i, m, v=generalHubbleValue: some_parameter_changed("hubble", v.get()))
generalHubbleEntry = Tk.Entry(generalPanel, textvariable=generalHubbleValue, width=5, state="disabled", bg="white")
generalHubbleEntry.grid(column=1, row=3, sticky=Tk.W)
generalBalloon.bind(generalHubbleEntry, "Hubble constant.") ### FIXME z or zero???
Tk.Label(generalPanel, text="km/sec/Mpc", width=9).grid(column=2, row=3, sticky=Tk.W)

# Solar absolute magnitude
Tk.Label(generalPanel, text=u"     M\u209b\u1d64\u2099 ", font=font11, width=6).grid(column=0, row=4, sticky=Tk.E)
generalSunMagValue = Tk.StringVar()
generalSunMagValue.set(5.45)
generalSunMagValue.trace("w", lambda n, i, m, v=generalSunMagValue: some_parameter_changed("Msun", v.get()))
generalSunMagEntry = Tk.Entry(generalPanel, textvariable=generalSunMagValue, width=5, state="disabled", bg="white")
generalSunMagBalloon = Balloon(generalPanel)
generalSunMagBalloon.bind(generalSunMagEntry, "Solar absolute magnitude.")
generalSunMagEntry.grid(column=1, row=4, sticky=Tk.W)
Tk.Label(generalPanel, text="mag").grid(column=2, row=4, sticky=Tk.W)


def band_selected(*args):
    global mSunBands
    if generalBandValue.get() != "---":
        generalSunMagValue.set(mSunBands[generalBandValue.get()])
generalBandValue = Tk.StringVar()
generalBandValue.set("Straizys B (= Johnson) Vega")
generalBandCBox = Tk.OptionMenu(generalPanel, generalBandValue, *mSunBandsList)
generalBandCBox.grid(column=0, row=5, sticky=Tk.W, columnspan=3)
generalBandValue.trace("w", band_selected)

#########################
#  Parameters of bulge  #
#########################

# Include bulge
bulgePanel = Tk.Frame(rightPanel, pady=5)
bulgeBalloon = Balloon(bulgePanel)
bulgePanel.grid(column=0, row=2)
includeBulge = Tk.IntVar()
includeBulge.set(0)
includeBulge.trace("w", lambda n, i, m, v=includeBulge: some_parameter_changed("bInclude", v.get()))
includeBulgeCButton = Tk.Checkbutton(bulgePanel, text="Bulge", variable=includeBulge, state="disabled")
includeBulgeCButton.grid(column=0, row=0, columnspan=2)
bulgeBalloon.bind(includeBulgeCButton, "Include bulge in the computation.")

# Bulge effective brightness entry
Tk.Label(bulgePanel, text=u"      \u03bc\u2091", font=font11, width=6).grid(column=0, row=1, sticky=Tk.E)
bulgeEffSurfBriValue = Tk.StringVar()
bulgeEffSurfBriValue.set("99.99")
bulgeEffSurfBriValue.trace("w", lambda n, i, m, v=bulgeEffSurfBriValue: some_parameter_changed("bSurfBri", v.get()))
bulgeEffSurfBriEntry = Tk.Entry(bulgePanel, textvariable=bulgeEffSurfBriValue, width=5, state="disabled", bg="white")
bulgeEffSurfBriEntry.grid(column=1, row=1, sticky=Tk.W)
Tk.Label(bulgePanel, text=u"mag/\u25a1''       ", width=9).grid(column=2, row=1, sticky=Tk.W)
bulgeBalloon.bind(bulgeEffSurfBriEntry, "Bulge effective brightness.")

# Bulge Sersic index
Tk.Label(bulgePanel, text="n  ", font=font11).grid(column=0, row=2, sticky=Tk.E)
bulgeSersicIndexValue = Tk.StringVar()
bulgeSersicIndexEntry = Tk.Entry(bulgePanel, textvariable=bulgeSersicIndexValue, width=5, state="disabled", bg="white")
bulgeSersicIndexEntry.grid(column=1, row=2, sticky=Tk.W)
bulgeSersicIndexValue.set("4.0")
bulgeSersicIndexValue.trace("w", lambda n, i, m, v=bulgeSersicIndexValue: some_parameter_changed("bSersic", v.get()))
bulgeBalloon.bind(bulgeSersicIndexEntry, u"Bulge S\u00E9rsic index.")

# Bulge effective radius
Tk.Label(bulgePanel, text=u"r\u2091\u2009 ", font=font11).grid(column=0, row=3, sticky=Tk.E)
bulgeEffRadiusValue = Tk.StringVar()
bulgeEffRadiusValue.set("0.00")
bulgeEffRadiusValue.trace("w", lambda n, i, m, v=bulgeEffRadiusValue: some_parameter_changed("bEffRad", v.get()))
bulgeEffRadiusEntry = Tk.Entry(bulgePanel, textvariable=bulgeEffRadiusValue, width=5, state="disabled", bg="white")
bulgeEffRadiusEntry.grid(column=1, row=3, sticky=Tk.W)
Tk.Label(bulgePanel, text="''").grid(column=2, row=3, sticky=Tk.W)
bulgeBalloon.bind(bulgeEffRadiusEntry, "Bulge effective radius in arcseconds.")

# Axis ratio
Tk.Label(bulgePanel, text="    b/a").grid(column=0, row=5)
bulgeAxisRatioValue = Tk.StringVar()
bulgeAxisRatioValue.set("1.0") # Default value for face-on disc
bulgeAxisRatioEntry = Tk.Entry(bulgePanel, textvariable=bulgeAxisRatioValue, width=5, state="disabled", bg="white")
bulgeAxisRatioEntry.grid(column=1, row=5, sticky=Tk.W)
bulgeAxisRatioValue.trace("w", lambda n, i, m, v=bulgeAxisRatioValue: some_parameter_changed("dAxisRatio", v.get()))
bulgeBalloon.bind(bulgeAxisRatioEntry, """Bulge minor to major axis ratio (b/a=1 means
bulge with circular isophotes).""")

Tk.Label(bulgePanel, text="    M/L").grid(column=0, row=6)
bulgeMLratioValue = Tk.StringVar()
bulgeMLratioValue.set("4.00")
bulgeMLratioEntry = Tk.Spinbox(bulgePanel,
                               textvariable=bulgeMLratioValue,
                               width=5,
                               state="disabled",
                               from_=0.1,
                               to=50,
                               increment=0.1,
                               bg="white")
bulgeMLratioValue.trace("w", lambda n, i, m, v=bulgeMLratioValue: some_parameter_changed("bulgeML", v.get()))
bulgeMLratioEntry.grid(column=1, row=6, sticky=Tk.W)
bulgeMLratioEntry.bind("<Button-4>", mouse_wheel_up)
bulgeMLratioEntry.bind("<Button-5>", mouse_wheel_down)
bulgeBalloon.bind(bulgeMLratioEntry, "Bulge mass-to-light ratio.")

##########################
#   Parameters of disk   #
##########################
diskPanel = Tk.Frame(rightPanel, pady=5)
diskPanel.grid(column=0, row=3)
diskBalloon = Balloon(diskPanel)

includeDisk = Tk.IntVar()
includeDisk.set(0)
includeDisk.trace("w", lambda n, i, m, v=includeDisk: some_parameter_changed("dInclude", v.get()))
includeDiskCButton = Tk.Checkbutton(diskPanel, text="Disk", variable=includeDisk, state="disabled")
includeDiskCButton.grid(column=0, row=0, columnspan=2)
diskBalloon.bind(includeDiskCButton, "Include disk in the computation.")

# Disc central surface brightness
Tk.Label(diskPanel, text=u"       \u03bc\u2080 ", font=font11, width=6).grid(column=0, row=1, sticky=Tk.E)
diskCenSurfBriValue = Tk.StringVar()
diskCenSurfBriValue.set("99.99")
diskCenSurfBriEntry = Tk.Entry(diskPanel, textvariable=diskCenSurfBriValue, width=5, state="disabled", bg="white")
diskCenSurfBriEntry.grid(column=1, row=1, sticky=Tk.W)
diskCenSurfBriValue.trace("w", lambda n, i, m, v=diskCenSurfBriValue: some_parameter_changed("dSurfBri", v.get()))
Tk.Label(diskPanel, text=u"mag/\u25a1''      ", width=9).grid(column=2, row=1, sticky=Tk.W)
diskBalloon.bind(diskCenSurfBriEntry, "Disk central surface brightness.")

# Disc exponential scale
Tk.Label(diskPanel, text="      h", font=font11).grid(column=0, row=2)
diskExpScaleValue = Tk.StringVar()
diskExpScaleValue.set("0.00")
diskExpScaleEntry = Tk.Entry(diskPanel, textvariable=diskExpScaleValue, width=5, state="disabled", bg="white")
diskExpScaleEntry.grid(column=1, row=2, sticky=Tk.W)
diskExpScaleValue.trace("w", lambda n, i, m, v=diskExpScaleValue: some_parameter_changed("dExpScale", v.get()))
Tk.Label(diskPanel, text="''").grid(column=2, row=2, sticky=Tk.W)
diskBalloon.bind(diskExpScaleEntry, "Disk exponential scalelength.")

# Disc axis ratio
Tk.Label(diskPanel, text="      b/a").grid(column=0, row=3)
diskAxisRatioValue = Tk.StringVar()
diskAxisRatioValue.set("1.0") # Default value for face-on disc
diskAxisRatioEntry = Tk.Entry(diskPanel, textvariable=diskAxisRatioValue, width=5, state="disabled", bg="white")
diskAxisRatioEntry.grid(column=1, row=3, sticky=Tk.W)
diskAxisRatioValue.trace("w", lambda n, i, m, v=diskAxisRatioValue: some_parameter_changed("dAxisRatio", v.get()))
diskBalloon.bind(diskAxisRatioEntry, "Disk minor to major axis ratio.")

# Disc thickness
Tk.Label(diskPanel, text=u"    z\u2080/h ", font=font11).grid(column=0, row=4)
diskThicknessValue = Tk.StringVar()
diskThicknessValue.set("0.20") 
diskThicknessEntry = Tk.Entry(diskPanel, textvariable=diskThicknessValue, width=5, state="disabled", bg="white")
diskThicknessEntry.grid(column=1, row=4, sticky=Tk.W)
diskThicknessValue.trace("w", lambda n, i, m, v=diskThicknessValue: some_parameter_changed("dThickness", v.get()))
diskBalloon.bind(diskThicknessEntry, u"""The ratio of the disk scaleheight z\u2080 to the disk exponential
scalelength h (internal thickness of the disk).""")

# Disc M-to-L ratio
Tk.Label(diskPanel, text="     M/L").grid(column=0, row=5)
diskMLratioValue = Tk.StringVar()
diskMLratioValue.set("3.00")
diskMLratioEntry = Tk.Spinbox(diskPanel,
                              textvariable=diskMLratioValue,
                              width=5,
                              state="disabled",
                              from_=0.1,
                              to=50,
                              increment=0.1,
                              bg="white")
diskMLratioValue.trace("w", lambda n, i, m, v=diskMLratioValue: some_parameter_changed("diskML", v.get()))
diskMLratioEntry.grid(column=1, row=5, sticky=Tk.W)
diskMLratioEntry.bind("<Button-4>", mouse_wheel_up)
diskMLratioEntry.bind("<Button-5>", mouse_wheel_down)
diskBalloon.bind(diskMLratioEntry, "Disk mass to light ratio.")

###########################
#   Parameters of halo    #
###########################

haloPanel = Tk.Frame(rightPanel, pady=5)
haloPanel.grid(column=0, row=4)
haloBalloon = Balloon(haloPanel)

includeHalo = Tk.IntVar()
includeHalo.set(0)
includeHalo.trace("w", lambda n, i, m, v=includeHalo: some_parameter_changed("hInclude", v.get()))
includeHaloCButton = Tk.Checkbutton(haloPanel, text="Halo", variable=includeHalo, state="disabled")
includeHaloCButton.grid(column=0, row=0, columnspan=2)
haloBalloon.bind(includeHaloCButton, "Include halo in the computation.")

# Halo type
haloModelValue = Tk.StringVar()
haloModelValue.set("isoterm")
haloModelValue.trace("w", lambda n, i, m, v=haloModelValue: some_parameter_changed("haloModel", v.get()))
haloFirstParamLabel = Tk.Label(haloPanel, text='Rc', width=5)
haloSecondParamLabel = Tk.Label(haloPanel, text=u'V(\u221E)', font=font11, width=5)

# We have to allocate these two entries here, before their 'griding' because
# we are needed them to bind balloons for proper description
# of their parameters (balloons have to depend on selected model). 
haloFirstParamValue = Tk.StringVar()
haloFirstParamEntry = Tk.Entry(haloPanel, textvariable=haloFirstParamValue, width=5, state="disabled", bg="white")
haloSecondParamValue = Tk.StringVar()
haloSecondParamEntry = Tk.Entry(haloPanel, textvariable=haloSecondParamValue, width=5, state="disabled", bg="white")

# Radiobuttons to select halo model.
isotermHaloRadiobutton = Tk.Radiobutton(haloPanel, 
                                        text="isoterm", 
                                        variable=haloModelValue, 
                                        value="isoterm", 
                                        state="disabled", 
                                        width=5,
                                        command=lambda : [haloFirstParamLabel.config(text="Rc"), 
                                                          haloSecondParamLabel.config(text=u'V(\u221E)', font=font11),
                                                          haloBalloon.bind(haloFirstParamEntry, "Core radius."),
                                                          haloBalloon.bind(haloSecondParamEntry, "Velocity at infinity.")])
isotermHaloRadiobutton.grid(column=0, row=1)
NFWHaloRadiobutton = Tk.Radiobutton(haloPanel,
                                    text="NFW",
                                    variable=haloModelValue,
                                    width=3,
                                    value="NFW", 
                                    state="disabled",
                                    command=lambda : [haloFirstParamLabel.config(text="C"),
                                                      haloSecondParamLabel.config(text="V200"),
                                                      haloBalloon.bind(haloFirstParamEntry, "Consentration parameter."),
                                                      haloBalloon.bind(haloSecondParamEntry, "Velocity at the virial radius.")])
NFWHaloRadiobutton.grid(column=1, row=1)
haloBalloon.bind(isotermHaloRadiobutton, "Halo type: isothermal halo.")
haloBalloon.bind(NFWHaloRadiobutton, "Halo type: Navarro Frenk White profile.")
haloBalloon.bind(haloFirstParamEntry, "Core radius.")
haloBalloon.bind(haloSecondParamEntry, "Velocity at infinity.")

# AC checkbutton
haloIncludeAC = Tk.IntVar()
haloIncludeAC.set(0)
haloIncludeAC.trace("w", lambda n, i, m, v=haloIncludeAC: some_parameter_changed("includeAC", v.get()))
haloACCheckbutton = Tk.Checkbutton(haloPanel, text="AC", variable=haloIncludeAC, state="disabled")
haloACCheckbutton.grid(column=2, row=1)
haloBalloon.bind(haloACCheckbutton, """Take into account the adiabatic contraction of the halo.
Warning: the computation with this mode turned on
will take considerably longer time.""")

# Place allocated before entries and stuff around them
haloFirstParamLabel.grid(column=0, row=2)
haloFirstParamValue.trace("w", lambda n, i, m, v=haloFirstParamValue: some_parameter_changed("haloFirst", v.get()))
haloFirstParamEntry.grid(column=1, row=2, sticky=Tk.W)

haloSecondParamLabel.grid(column=0, row=3)
haloSecondParamValue.trace("w", lambda n, i, m, v=haloSecondParamValue: some_parameter_changed("haloSecond", v.get()))
haloSecondParamEntry.grid(column=1, row=3, sticky=Tk.W)
Tk.Label(haloPanel, text="Km/sec").grid(column=2, row=3)


# Button for computation running
runPanel = Tk.Frame(rightPanel)
runPanel.grid(column=0, row=5)
runButton = Tk.Button(runPanel, text="Compute!", state="disabled", command=runComputation)
runButton.grid(column=0, row=0)

############################################################
#                    End of right panel                   #
############################################################



############################################################
#                Creating graph stuff                      #
############################################################

mainGraph = pylab.Figure(figsize=(6, 4), dpi=100)
canvas = FigureCanvasTkAgg(mainGraph, master=master)
toolbar = NavigationToolbar2TkAgg(canvas, master)
toolbar.update()
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

############################################################
#                End of the graph stuff                    #
############################################################


Tk.mainloop()

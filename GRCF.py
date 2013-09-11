#! /usr/bin/env python

import pylab

import Tkinter as Tk
import tkFileDialog
import tkMessageBox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

from GRCFlibs.GRCFmathFunctions import *
from GRCFlibs.GRCFifaceFunctions import *


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
    generalInclinationEntry.config(state="normal")
    generalSunMagEntry.config(state="normal")
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
    gParams["incl"] = generalInclinationValue.get()
    gParams["scale"] = generalScaleValue.get()
    gParams["hubble"] = generalHubbleValue.get()
    gParams["Msun"] = generalSunMagValue.get()
    bParams = {}
    bParams["include"] = includeBulge.get()
    bParams["effSurfBri"] = bulgeEffSurfBriValue.get()
    bParams["sersicIndex"] = bulgeSersicIndexValue.get()
    bParams["effRadius"] = bulgeEffRadiusValue.get()
#    bParams["oblateness"] = bulgeOblatenessValue.get()
    bParams["MLratio"] = bulgeMLratioValue.get()
    dParams = {}
    dParams["include"] = includeDisk.get()
    dParams["cenSurfBri"] = diskCenSurfBriValue.get()
    dParams["expScale"] = diskExpScaleValue.get()
    dParams["thickness"] = diskThicknessValue.get()
    dParams["MLratio"] = diskMLratioValue.get()
    hParams = {}
    hParams["include"] = includeHalo.get()
    hParams["firstParam"] = haloFirstParamValue.get()
    hParams["secondParam"] = haloSecondParamValue.get()
    hParams["model"] = haloModelValue.get()
    return gParams, bParams, dParams, hParams


def setValuesToAllFields(params):
    if params[0] is None:
        return
    gParams = params[0]
    bParams = params[1]
    dParams = params[2]
    hParams = params[3]
    generalInclinationValue.set(gParams["incl"])
    generalScaleValue.set(gParams["scale"])
    generalSunMagValue.set(gParams["Msun"])
    generalHubbleValue.set(gParams["hubble"])
    includeBulge.set(bParams["include"])
    bulgeEffSurfBriValue.set(bParams["effSurfBri"])
    bulgeSersicIndexValue.set(bParams["sersicIndex"])
    bulgeEffRadiusValue.set(bParams["effRadius"])
#    bulgeOblatenessValue.set(bParams["oblateness"])
    bulgeMLratioValue.set(bParams["MLratio"])
    includeDisk.set(dParams["include"])
    diskCenSurfBriValue.set(dParams["cenSurfBri"])
    diskExpScaleValue.set(dParams["expScale"])
    diskThicknessValue.set(dParams["thickness"])
    diskMLratioValue.set(dParams["MLratio"])
    includeHalo.set(hParams["include"])
    haloFirstParamValue.set(hParams["firstParam"])
    haloSecondParamValue.set(hParams["secondParam"])
    haloModelValue.set(hParams["model"])

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
    if parameter == "incl":
        rotCurve.deproject(newValue)
    if parameter == "scale":
        rotCurve.reScale(newValue)
    if parameter == "bInclude":
        onoffPanel(bulgePanel, newValue)
    if parameter == "dInclude":
        onoffPanel(diskPanel, newValue)
    if parameter == "hInclude":
        onoffPanel(haloPanel, newValue)
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
master.title("Galaxy Rotation Curve Fit")
master.geometry(("950x550"))

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
colouredPaint.trace("w", lambda n, i, m, v=colouredPaint:some_parameter_changed("colouredPaint", v.get()))
showChiSquared = Tk.IntVar()
showChiSquared.set(1)
viewMenu.add_checkbutton(label="Chi squared",
                         variable=showChiSquared,
                         state="disabled")
showChiSquared.trace("w", lambda n, i, m, v=showChiSquared:some_parameter_changed("showChiSquared", v.get()))
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


# general parameters
generalPanel = Tk.Frame(rightPanel, pady=5)
generalPanel.grid(column=0, row=1)
Tk.Label(generalPanel, text="inclination").grid(column=0, row=0)
generalInclinationValue = Tk.StringVar()
generalInclinationValue.set("90.0")
generalInclinationEntry = Tk.Spinbox(generalPanel, 
                                     textvariable=generalInclinationValue, 
                                     width=5, 
                                     state="disabled", 
                                     from_=1, 
                                     to=90, 
                                     increment=0.1,
                                     bg="white")
generalInclinationEntry.grid(column=1, row=0, sticky=Tk.W)
generalInclinationEntry.bind("<Button-4>", mouse_wheel_up)
generalInclinationEntry.bind("<Button-5>", mouse_wheel_down)
generalInclinationValue.trace("w", 
                              lambda n, i, m, v=generalInclinationValue: some_parameter_changed("incl", v.get()))
Tk.Label(generalPanel, text=" deg             ").grid(column=2, row=0)

Tk.Label(generalPanel, text="scale").grid(column=0, row=1)
generalScaleValue = Tk.StringVar()
generalScaleValue.set("1.00")
generalScaleValue.trace("w", 
                        lambda n, i, m, v=generalScaleValue: some_parameter_changed("scale", v.get()))
generalScaleEntry = Tk.Entry(generalPanel, textvariable=generalScaleValue, width=5, state="disabled", bg="white")
generalScaleEntry.grid(column=1, row=1, sticky=Tk.W)
Tk.Label(generalPanel, text="kpc/arcsec").grid(column=2, row=1)

# Hubble parameter value
Tk.Label(generalPanel, text="H0").grid(column=0, row=2)
generalHubbleValue = Tk.StringVar()
generalHubbleValue.set("67.0")
generalHubbleValue.trace("w", 
                        lambda n, i, m, v=generalHubbleValue: some_parameter_changed("hubble", v.get()))
generalHubbleEntry = Tk.Entry(generalPanel, textvariable=generalHubbleValue, width=5, state="disabled", bg="white")
generalHubbleEntry.grid(column=1, row=2, sticky=Tk.W)
Tk.Label(generalPanel, text="km/sec/Mpc").grid(column=2, row=2)

# Solar absolute magnitude
Tk.Label(generalPanel, text="M_sun").grid(column=0, row=3)
generalSunMagValue = Tk.StringVar()
generalSunMagValue.set(5.45)
generalSunMagValue.trace("w", lambda n, i, m, v=generalSunMagValue: some_parameter_changed("Msun", v.get()))
generalSunMagEntry = Tk.Entry(generalPanel, textvariable=generalSunMagValue, width=5, state="disabled", bg="white")
generalSunMagEntry.grid(column=1, row=3, sticky=Tk.W)
Tk.Label(generalPanel, text="mag            ").grid(column=2, row=3)


def band_selected(*args):
    global mSunBands
    if generalBandValue.get() != "---":
        generalSunMagValue.set(mSunBands[generalBandValue.get()])
generalBandValue = Tk.StringVar()
generalBandValue.set("Straizys B (= Johnson) Vega")
generalBandCBox = Tk.OptionMenu(generalPanel, generalBandValue, *mSunBandsList)
generalBandCBox.grid(column=0, row=4, sticky=Tk.W, columnspan=3)
generalBandValue.trace("w", band_selected)

# Parameters of bulge
bulgePanel = Tk.Frame(rightPanel, pady=5)
bulgePanel.grid(column=0, row=2)
includeBulge = Tk.IntVar()
includeBulge.set(0)
includeBulge.trace("w", lambda n, i, m, v=includeBulge: some_parameter_changed("bInclude", v.get()))
includeBulgeCButton = Tk.Checkbutton(bulgePanel, text="Bulge", variable=includeBulge, state="disabled")
includeBulgeCButton.grid(column=0, row=0, columnspan=2)

Tk.Label(bulgePanel, text="Eff.Surf.bri").grid(column=0, row=1)
bulgeEffSurfBriValue = Tk.StringVar()
bulgeEffSurfBriValue.set("99.99")
bulgeEffSurfBriValue.trace("w", lambda n, i, m, v=bulgeEffSurfBriValue: some_parameter_changed("bSurfBri", v.get()))
bulgeEffSurfBriEntry = Tk.Entry(bulgePanel, textvariable=bulgeEffSurfBriValue, width=5, state="disabled", bg="white")
bulgeEffSurfBriEntry.grid(column=1, row=1, sticky=Tk.W)
Tk.Label(bulgePanel, text="mag/sq.arcsec").grid(column=2, row=1)

Tk.Label(bulgePanel, text="Sersic index").grid(column=0, row=2)
bulgeSersicIndexValue = Tk.StringVar()
bulgeSersicIndexEntry = Tk.Entry(bulgePanel, textvariable=bulgeSersicIndexValue, width=5, state="disabled", bg="white")
bulgeSersicIndexEntry.grid(column=1, row=2, sticky=Tk.W)
bulgeSersicIndexValue.set("4.0")
bulgeSersicIndexValue.trace("w", lambda n, i, m, v=bulgeSersicIndexValue: some_parameter_changed("bSersic", v.get()))

Tk.Label(bulgePanel, text="R_eff").grid(column=0, row=3)
bulgeEffRadiusValue = Tk.StringVar()
bulgeEffRadiusValue.set("0.00")
bulgeEffRadiusValue.trace("w", lambda n, i, m, v=bulgeEffRadiusValue: some_parameter_changed("bEffRad", v.get()))
bulgeEffRadiusEntry = Tk.Entry(bulgePanel, textvariable=bulgeEffRadiusValue, width=5, state="disabled", bg="white")
bulgeEffRadiusEntry.grid(column=1, row=3, sticky=Tk.W)
Tk.Label(bulgePanel, text="arcsec            ").grid(column=2, row=3)

#Tk.Label(bulgePanel, text="q").grid(column=0, row=4)
#bulgeOblatenessValue = Tk.StringVar()
#bulgeOblatenessValue.set("1.00")
#bulgeOblatenessEntry = Tk.Entry(bulgePanel, textvariable=bulgeOblatenessValue, width=5, state="disabled", bg="white")
#bulgeOblatenessEntry.grid(column=1, row=4, sticky=Tk.W)

Tk.Label(bulgePanel, text="M/L").grid(column=0, row=5)
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
bulgeMLratioEntry.grid(column=1, row=5, sticky=Tk.W)
bulgeMLratioEntry.bind("<Button-4>", mouse_wheel_up)
bulgeMLratioEntry.bind("<Button-5>", mouse_wheel_down)


# Parameters of disk
diskPanel = Tk.Frame(rightPanel, pady=5)
diskPanel.grid(column=0, row=3)

includeDisk = Tk.IntVar()
includeDisk.set(0)
includeDisk.trace("w", lambda n, i, m, v=includeDisk: some_parameter_changed("dInclude", v.get()))
includeDiskCButton = Tk.Checkbutton(diskPanel, text="Disk", variable=includeDisk, state="disabled")
includeDiskCButton.grid(column=0, row=0, columnspan=2)

Tk.Label(diskPanel, text="    Surf.Bri   ").grid(column=0, row=1)
diskCenSurfBriValue = Tk.StringVar()
diskCenSurfBriValue.set("99.99")
diskCenSurfBriEntry = Tk.Entry(diskPanel, textvariable=diskCenSurfBriValue, width=5, state="disabled", bg="white")
diskCenSurfBriEntry.grid(column=1, row=1, sticky=Tk.W)
diskCenSurfBriValue.trace("w", lambda n, i, m, v=diskCenSurfBriValue: some_parameter_changed("dSurfBri", v.get()))
Tk.Label(diskPanel, text="mag/sq.arcsec").grid(column=2, row=1)

Tk.Label(diskPanel, text="Exp. scale").grid(column=0, row=2)
diskExpScaleValue = Tk.StringVar()
diskExpScaleValue.set("0.00")
diskExpScaleEntry = Tk.Entry(diskPanel, textvariable=diskExpScaleValue, width=5, state="disabled", bg="white")
diskExpScaleEntry.grid(column=1, row=2, sticky=Tk.W)
diskExpScaleValue.trace("w", lambda n, i, m, v=diskExpScaleValue: some_parameter_changed("dExpScale", v.get()))
Tk.Label(diskPanel, text="arcsec            ").grid(column=2, row=2)

Tk.Label(diskPanel, text="z0").grid(column=0, row=3)
diskThicknessValue = Tk.StringVar()
diskThicknessValue.set("0.00")
diskThicknessEntry = Tk.Entry(diskPanel, textvariable=diskThicknessValue, width=5, state="disabled", bg="white")
diskThicknessEntry.grid(column=1, row=3, sticky=Tk.W)
diskThicknessValue.trace("w", lambda n, i, m, v=diskThicknessValue: some_parameter_changed("dThickness", v.get()))
Tk.Label(diskPanel, text="* h                  ").grid(column=2, row=3)

Tk.Label(diskPanel, text="M/L").grid(column=0, row=4)
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
diskMLratioEntry.grid(column=1, row=4, sticky=Tk.W)
diskMLratioEntry.bind("<Button-4>", mouse_wheel_up)
diskMLratioEntry.bind("<Button-5>", mouse_wheel_down)


# Parameters of halo
haloPanel = Tk.Frame(rightPanel, pady=5)
haloPanel.grid(column=0, row=4)
includeHalo = Tk.IntVar()
includeHalo.set(0)
includeHalo.trace("w", lambda n, i, m, v=includeHalo: some_parameter_changed("hInclude", v.get()))
includeHaloCButton = Tk.Checkbutton(haloPanel, text="Halo", variable=includeHalo, state="disabled")
includeHaloCButton.grid(column=0, row=0, columnspan=1)
haloModelValue = Tk.StringVar()
haloModelValue.set("isoterm")
haloModelValue.trace("w", lambda n, i, m, v=haloModelValue: some_parameter_changed("haloModel", v.get()))
haloFirstParamLabel = Tk.Label(haloPanel, text='Rc')
haloSecondParamLabel = Tk.Label(haloPanel, text='V(inf)')
isotermHaloRadiobutton = Tk.Radiobutton(haloPanel, 
                                        text="isoterm", 
                                        variable=haloModelValue, 
                                        value="isoterm", 
                                        state="disabled", 
                                        command=lambda : [haloFirstParamLabel.config(text="Rc"), haloSecondParamLabel.config(text="V(inf)")])
isotermHaloRadiobutton.grid(column=1, row=0)
NFWHaloRadiobutton = Tk.Radiobutton(haloPanel,
                                    text="NFW",
                                    variable=haloModelValue,
                                    value="NFW", 
                                    state="disabled",
                                    command=lambda : [haloFirstParamLabel.config(text="C"), haloSecondParamLabel.config(text="V200")])
NFWHaloRadiobutton.grid(column=2, row=0)

haloFirstParamLabel.grid(column=0, row=1)
haloFirstParamValue = Tk.StringVar()
haloFirstParamValue.trace("w", lambda n, i, m, v=haloFirstParamValue: some_parameter_changed("haloFirst", v.get()))
haloFirstParamEntry = Tk.Entry(haloPanel, textvariable=haloFirstParamValue, width=5, state="disabled", bg="white")
haloFirstParamEntry.grid(column=1, row=1)
haloSecondParamLabel.grid(column=0, row=2)

haloSecondParamValue = Tk.StringVar()
haloSecondParamValue.trace("w", lambda n, i, m, v=haloSecondParamValue: some_parameter_changed("haloSecond", v.get()))
haloSecondParamEntry = Tk.Entry(haloPanel, textvariable=haloSecondParamValue, width=5, state="disabled", bg="white")
haloSecondParamEntry.grid(column=1, row=2)
Tk.Label(haloPanel, text="Km/sec     ").grid(column=2, row=2)


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
#                  End graph stuff                         #
############################################################


Tk.mainloop()

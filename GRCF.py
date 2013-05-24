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
    rotCurve = GalaxyRotation(distance, velocity, sigma, float(generalScaleValue.get()), mainGraph, canvas)
    rotCurve.plot()
    generalInclinationEntry.config(state="normal")
    generalSunMagEntry.config(state="normal")
    generalScaleEntry.config(state="normal")
    includeDiskCButton.config(state="normal")
    includeBulgeCButton.config(state="normal")
    includeHaloCButton.config(state="normal")
    runButton.config(state="normal")

def runComputation():
    gParams = {}
    gParams["incl"] = generalInclinationValue.get()
    gParams["scale"] = generalScaleValue.get()
    gParams["Msun"] = generalSunMagValue.get()
    bParams = {}
    bParams["include"] = includeBulge.get()
    bParams["effSurfBri"] = bulgeEffSurfBriValue.get()
    bParams["sersicIndex"] = bulgeSersicIndexValue.get()
    bParams["effRadius"] = bulgeEffRadiusValue.get()
    bParams["oblateness"] = bulgeOblatenessValue.get()
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
    # Are values of all parameters correct?
    resOfCheck, failParam, reasonOfResult = checAllValues(gParams, bParams, dParams, hParams)
    # If at least one parameter is incorrect, show popup window and stop computation
    if resOfCheck is False:
            tkMessageBox.showerror("Value error", "%s value is incorrect \n (%s)" % (failParam, reasonOfResult))
            return False
    # If all is Ok
    runButton.config(state="disabled")
    rotCurve.makeComputation(gParams, bParams, dParams, hParams)
    runButton.config(state="normal")


# Creating the main window
master = Tk.Tk()
master.title("Galaxy Rotation Curve Fit")
master.geometry(("950x550"))


############################################################
#                Creating menu                             #
############################################################

menubar = Tk.Menu(master)
menubar.add_command(label="Load file", command=loadVelocityData)
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
generalInclinationEntry = Tk.Spinbox(generalPanel, textvariable=generalInclinationValue, width=5, state="disabled", from_=1, to=90, increment=0.1)
generalInclinationEntry.grid(column=1, row=0, sticky=Tk.W)
generalInclinationEntry.bind("<Button-4>", mouse_wheel_up)
generalInclinationEntry.bind("<Button-5>", mouse_wheel_down)
generalInclinationValue.trace("w", lambda n, i, m, v=generalInclinationValue: rotCurve.deproject(v.get()))
Tk.Label(generalPanel, text=" deg             ").grid(column=2, row=0)
Tk.Label(generalPanel, text="scale").grid(column=0, row=1)
generalScaleValue = Tk.StringVar()
generalScaleValue.set("1.00")
generalScaleValue.trace("w", lambda n, i, m, v=generalScaleValue: rotCurve.reScale(v.get()))
generalScaleEntry = Tk.Entry(generalPanel, textvariable=generalScaleValue, width=5, state="disabled")
generalScaleEntry.grid(column=1, row=1, sticky=Tk.W)
Tk.Label(generalPanel, text="kpc/arcsec").grid(column=2, row=1)
Tk.Label(generalPanel, text="M_sun").grid(column=0, row=2)
generalSunMagValue = Tk.StringVar()
generalSunMagValue.set(5.11)
generalSunMagEntry = Tk.Entry(generalPanel, textvariable=generalSunMagValue, width=5, state="disabled")
generalSunMagEntry.grid(column=1, row=2, sticky=Tk.W)
Tk.Label(generalPanel, text="mag            ").grid(column=2, row=2)


#rrr = {"one": 1, "two": 2, "three": 3}
#def callback(*args):
#    global rrr
#    generalSunMagValue.set(rrr[generalSunMagValue1.get()])
#generalSunMagValue1 = Tk.StringVar()
#generalSunMagCBox = Tk.OptionMenu(generalPanel, generalSunMagValue1, *rrr.keys())
#generalSunMagCBox.grid(column=1, row=3, sticky=Tk.W)
#generalSunMagValue1.trace("w", callback)

# Parameters of bulge
bulgePanel = Tk.Frame(rightPanel, pady=5)
bulgePanel.grid(column=0, row=2)
includeBulge = Tk.IntVar()
includeBulge.set(0)
includeBulge.trace("w", lambda n, i, m, v=includeBulge: onoffPanel(bulgePanel, v.get()))
includeBulgeCButton = Tk.Checkbutton(bulgePanel, text="Bulge", variable=includeBulge, state="disabled")
includeBulgeCButton.grid(column=0, row=0, columnspan=2)
Tk.Label(bulgePanel, text="Eff.Surf.bri").grid(column=0, row=1)
bulgeEffSurfBriValue = Tk.StringVar()
bulgeEffSurfBriValue.set("99.99")
bulgeEffSurfBriEntry = Tk.Entry(bulgePanel, textvariable=bulgeEffSurfBriValue, width=5, state="disabled")
bulgeEffSurfBriEntry.grid(column=1, row=1, sticky=Tk.W)
Tk.Label(bulgePanel, text="mag/sq.arcsec").grid(column=2, row=1)
Tk.Label(bulgePanel, text="Sersic index").grid(column=0, row=2)
bulgeSersicIndexValue = Tk.StringVar()
bulgeSersicIndexEntry = Tk.Entry(bulgePanel, textvariable=bulgeSersicIndexValue, width=5, state="disabled")
bulgeSersicIndexEntry.grid(column=1, row=2, sticky=Tk.W)
bulgeSersicIndexValue.set("4.0")
Tk.Label(bulgePanel, text="R_eff").grid(column=0, row=3)
bulgeEffRadiusValue = Tk.StringVar()
bulgeEffRadiusValue.set("0.00")
bulgeEffRadiusEntry = Tk.Entry(bulgePanel, textvariable=bulgeEffRadiusValue, width=5, state="disabled")
bulgeEffRadiusEntry.grid(column=1, row=3, sticky=Tk.W)
Tk.Label(bulgePanel, text="arcsec            ").grid(column=2, row=3)
Tk.Label(bulgePanel, text="q").grid(column=0, row=4)
bulgeOblatenessValue = Tk.StringVar()
bulgeOblatenessValue.set("1.00")
bulgeOblatenessEntry = Tk.Entry(bulgePanel, textvariable=bulgeOblatenessValue, width=5, state="disabled")
bulgeOblatenessEntry.grid(column=1, row=4, sticky=Tk.W)
Tk.Label(bulgePanel, text="M/L").grid(column=0, row=5)
bulgeMLratioValue = Tk.StringVar()
bulgeMLratioValue.set("4.00")
bulgeMLratioEntry = Tk.Spinbox(bulgePanel, textvariable=bulgeMLratioValue, width=5, state="disabled", from_=1, to=10, increment=0.1)
bulgeMLratioEntry.grid(column=1, row=5, sticky=Tk.W)
bulgeMLratioEntry.bind("<Button-4>", mouse_wheel_up)
bulgeMLratioEntry.bind("<Button-5>", mouse_wheel_down)


# Parameters of disk
diskPanel = Tk.Frame(rightPanel, pady=5)
diskPanel.grid(column=0, row=3)
includeDisk = Tk.IntVar()
includeDisk.set(0)
includeDisk.trace("w", lambda n, i, m, v=includeDisk: onoffPanel(diskPanel, v.get()))
includeDiskCButton = Tk.Checkbutton(diskPanel, text="Disk", variable=includeDisk, state="disabled")
includeDiskCButton.grid(column=0, row=0, columnspan=2)
Tk.Label(diskPanel, text="    Surf.Bri   ").grid(column=0, row=1)
diskCenSurfBriValue = Tk.StringVar()
diskCenSurfBriValue.set("99.99")
diskCenSurfBriEntry = Tk.Entry(diskPanel, textvariable=diskCenSurfBriValue, width=5, state="disabled")
diskCenSurfBriEntry.grid(column=1, row=1, sticky=Tk.W)
Tk.Label(diskPanel, text="mag/sq.arcsec").grid(column=2, row=1)
Tk.Label(diskPanel, text="Exp. scale").grid(column=0, row=2)
diskExpScaleValue = Tk.StringVar()
diskExpScaleValue.set("0.00")
diskExpScaleEntry = Tk.Entry(diskPanel, textvariable=diskExpScaleValue, width=5, state="disabled")
diskExpScaleEntry.grid(column=1, row=2, sticky=Tk.W)
Tk.Label(diskPanel, text="arcsec            ").grid(column=2, row=2)
Tk.Label(diskPanel, text="z0").grid(column=0, row=3)
diskThicknessValue = Tk.StringVar()
diskThicknessValue.set("0.00")
diskThicknessEntry = Tk.Entry(diskPanel, textvariable=diskThicknessValue, width=5, state="disabled")
diskThicknessEntry.grid(column=1, row=3, sticky=Tk.W)
Tk.Label(diskPanel, text="* h                  ").grid(column=2, row=3)
Tk.Label(diskPanel, text="M/L").grid(column=0, row=4)
diskMLratioValue = Tk.StringVar()
diskMLratioValue.set("3.00")
diskMLratioEntry = Tk.Spinbox(diskPanel, textvariable=diskMLratioValue, width=5, state="disabled", from_=1, to=10, increment=0.1)
diskMLratioEntry.grid(column=1, row=4, sticky=Tk.W)
diskMLratioEntry.bind("<Button-4>", mouse_wheel_up)
diskMLratioEntry.bind("<Button-5>", mouse_wheel_down)


# Parameters of halo
haloPanel = Tk.Frame(rightPanel, pady=5)
haloPanel.grid(column=0, row=4)
includeHalo = Tk.IntVar()
includeHalo.set(0)
includeHalo.trace("w", lambda n, i, m, v=includeHalo: onoffPanel(haloPanel, v.get()))
includeHaloCButton = Tk.Checkbutton(haloPanel, text="Halo", variable=includeHalo, state="disabled")
includeHaloCButton.grid(column=0, row=0, columnspan=1)
haloModelValue = Tk.StringVar()
haloModelValue.set("isoterm")
haloFirstParamLabel = Tk.Label(haloPanel, text='Rc')
isotermHaloRadiobutton = Tk.Radiobutton(haloPanel, 
                                        text="isoterm", 
                                        variable=haloModelValue, 
                                        value="isoterm", 
                                        state="disabled", 
                                        command=lambda : haloFirstParamLabel.config(text="Rc"))
isotermHaloRadiobutton.grid(column=1, row=0)
NFWHaloRadiobutton = Tk.Radiobutton(haloPanel,
                                    text="NFW",
                                    variable=haloModelValue,
                                    value="NFW", 
                                    state="disabled",
                                    command=lambda : haloFirstParamLabel.config(text="C"))
NFWHaloRadiobutton.grid(column=2, row=0)
haloFirstParamLabel.grid(column=0, row=1)
haloFirstParamValue = Tk.StringVar()
haloFirstParamEntry = Tk.Entry(haloPanel, textvariable=haloFirstParamValue, width=5, state="disabled")
haloFirstParamEntry.grid(column=1, row=1)
Tk.Label(haloPanel, text="V(inf)").grid(column=0, row=2)
haloSecondParamValue = Tk.StringVar()
haloSecondParamEntry = Tk.Entry(haloPanel, textvariable=haloSecondParamValue, width=5, state="disabled")
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

#! /usr/bin/env python

import Tkinter as Tk

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

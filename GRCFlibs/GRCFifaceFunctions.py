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
            if (c.winfo_class() == "Entry") or (c.winfo_class() == "Radiobutton"):
                c.config(state="normal")
    else:
        for c in panel.winfo_children():
            if (c.winfo_class() == "Entry") or (c.winfo_class() == "Radiobutton"):
                c.config(state="disabled")

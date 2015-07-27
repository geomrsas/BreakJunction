##### Required for plot fitting
import numpy

##### A Module for keeping track of time
import time

import random

import wx
import matplotlib
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

import matplotlib.pyplot as plt

##### A Customized Module to Send and Receive Data/Instructions to Instruments
from acquisition import *

##=========================================================================================================================================>> ARRAY COMMANDS <<=====##

##### Get the latest (last) value of a series (list) of values
def getLast(mylist):
	try:
		last = mylist[-1]
	except:
		last = float(0)

	return last

##### Get the next latest (next last) value of a series (list) of values
def getNextLast(mylist):
	try:
		nextLast = mylist[-2]
	except:
		nextLast = float(0)

	return nextLast

##### Calculate the conductance, perform a division-by-zero check
def calculateConductance(I,V):
	try:
		return float(I)/float(V)
	except:
		return float(0)

##### Calculate slope and intercept
def fit(I,V):
	if len(I) >= 2:
		x = numpy.array(V)
		y = numpy.array(I)
		f = numpy.polyfit(x,y,1)
	else:
		f = [0,0]

	# Return slope, intercept
	return f[0], f[1]


##======================================================================================================================================>> PLOTTING COMMANDS <<=====##

def plotData(T, V, I, G):

	I_mA = [i*1000 for i in I]
	G_renormed = [g/7.74809173E-5 for g in G]

	line1.set_xdata(V)
	line1.set_ydata(I_mA)
	line2.set_xdata(V)
	line2.set_ydata(G_renormed)

	ax1.relim()
	ax2.relim()

	ax1.autoscale_view()	
	ax2.autoscale_view()
	
	plot_panel.canvas.draw()
	plot_panel.canvas.flush_events()

##========================================================================================================================>> CORE JUNCTION BREAKING COMMANDS <<=====##

def MAIN(Event):
	start_btn.Disable()
	stop_btn.Enable()

	TimeElapsed = []
	Voltage = []
	Current = []
	Conductance = []

	startTime = time.time()
	
	path = "../BreakJunction4_Data/"
	filename = time.strftime("%Y-%m-%d-%H-%M-%S.csv", time.localtime())
	file_txt.SetValue(filename)
	dataFile = open(path + filename, "a")

	dataFile.write("TimeElapsed_s, Voltage_V, Current_A, Conductance_S\n")

	voltageIncStep = float( IncV_entry.GetValue() )*0.001
	voltageDecStep = float( DecV_entry.GetValue() )*0.001
	sensitivity = float( Sens_entry.GetValue() )	
	finalConductance = float( FinG_entry.GetValue() )

	amplifierSensitivity = 10**( -float( AmpS_entry.GetValue() ) )
	samplesPerDatum = Samp_entry.GetValue()
	stepDelay = float( Dely_entry.GetValue() )/1000

	expLoopIndex = 0
	while not stop_btn.GetValue():
		while len(Voltage) > 100:
			dataFile.write("%.5e" % TimeElapsed.pop(0) + ",")
			dataFile.write("%.5e" % Voltage.pop(0) + ",")
			dataFile.write("%.5e" % Current.pop(0) + ",")
			dataFile.write("%.5e" % Conductance.pop(0) + "\n")

		lastVoltage = getLast(Voltage)
		nextLastVoltage = getNextLast(Voltage)

		lastConductance = getLast(Conductance)
		nextLastConductance = getNextLast(Conductance)

		LineFit = fit(Current,Voltage)
		Iexpected = getLast(Voltage) * LineFit[0] + LineFit[1]

		try:
			f = 1-(1/float(1+lastVoltage*sensitivity))
		except:
			f = float(0)	# Default sensitivity value in case last voltage applied was zero

		if getLast(Current) < f*Iexpected and expLoopIndex > 5 and getLast(Voltage) - voltageDecStep > voltageDecStep:
			k = 0
			while k <= 10 and voltageDecStep < getLast(Voltage) - voltageDecStep:
				elapsed = time.time() - startTime
				TimeElapsed.append(elapsed)
				m, s = divmod(elapsed, 60)
				h, m = divmod(m, 60)
				elapsed_txt.SetValue("%d:%02d:%02d" % (h, m, s))
					
				voltage = getLast(Voltage) - voltageDecStep
				Voltage.append(voltage)
				setVoltage(voltage)
				
				raw_Voltage_readings = []
				if samplesPerDatum == 0:
					average_Voltage_reading = readVoltage()
				else:
					for i in range(samplesPerDatum):
						raw_Voltage_readings.append(readVoltage())
					average_Voltage_reading = float(sum(raw_Voltage_readings))/float(len(raw_Voltage_readings)) 
				current = -(amplifierSensitivity*(average_Voltage_reading - 0.000556542)) 
				Current.append(current)

				conductance = calculateConductance(current,voltage)
				Conductance.append(conductance)

				plotData(TimeElapsed, Voltage, Current, Conductance)
				time.sleep(stepDelay)

				k = k + 1	

		else:
			elapsed = time.time() - startTime
			TimeElapsed.append(elapsed)
			m, s = divmod(elapsed, 60)
			h, m = divmod(m, 60)
			elapsed_txt.SetValue("%d:%02d:%02d" % (h, m, s))

			voltage = getLast(Voltage) + voltageIncStep
			Voltage.append(voltage)
			setVoltage(voltage)

			raw_Voltage_readings = []
			if samplesPerDatum == 0:
				average_Voltage_reading = readVoltage()
			else:
				for i in range(samplesPerDatum):
					raw_Voltage_readings.append(readVoltage())
				average_Voltage_reading = float(sum(raw_Voltage_readings))/float(len(raw_Voltage_readings)) 
			current = -(amplifierSensitivity*(average_Voltage_reading - 0.000556542)) 
			Current.append(current)

			conductance = calculateConductance(current,voltage)
			Conductance.append(conductance)

			plotData(TimeElapsed, Voltage, Current, Conductance)
			time.sleep(stepDelay)

		if getLast(Conductance)/7.74809173E-5 < finalConductance and expLoopIndex > 100:
			print "Conductance reached Final"
			break

		print "%3.0f s, %4.3f V, %4.3f mA, %3.2f G0" %( getLast(TimeElapsed), getLast(Voltage), getLast(Current)*1000.0 , getLast(Conductance)/7.74809173E-5 )
		expLoopIndex = expLoopIndex + 1

	# At the end of the loop, immediately set voltage to zero.
	setVoltage(0.0)

	# Save the remaining data files
	while len(Voltage) > 0:
		dataFile.write("%.5e" % TimeElapsed.pop(0) + ",")
		dataFile.write("%.5e" % Voltage.pop(0) + ",")
		dataFile.write("%.5e" % Current.pop(0) + ",")
		dataFile.write("%.5e" % Conductance.pop(0) + "\n")
	
	start_btn.Enable()
	stop_btn.SetValue(False)
	stop_btn.Disable()


def QUIT(Event):
	# Deinitialize the Instruments so they can be used again under Spanish Acquisition.
	deinitializeInstruments()

	# Gets rid of the GUI Window
	target = Event.GetEventObject()
	target.Destroy()

##=========================================================================================================================>> CREATE USER INTERFACE COMMANDS <<=====##

def startme(Event):
	## TAKE INPUT VALUES
	print float( AmpS_entry.GetValue() )
	print float( IncV_entry.GetValue() )
	print float( DecV_entry.GetValue() )
	print float( Sens_entry.GetValue() )
	print float( FinG_entry.GetValue() )
	print float( Samp_entry.GetValue() )
	print float( Dely_entry.GetValue() )
	
	## SHOW OUTPUT VALUES
	file_txt.SetValue("2015-05-23-12-45-23.csv")
	elapsed_txt.SetValue("awefaweg")

	## ENABLE STOP BTN
	start_btn.Disable()
	stop_btn.Enable()

	num_plots = 0
	tstart = time.time()

	while time.time()-tstart < 10 and not stop_btn.GetValue():
		x = []
		y = []
		for i in range(100):
			x.extend([random.random()])
			y.extend([random.random()])
		plotme(x,y)
		num_plots = num_plots + 1

	print(num_plots)

	start_btn.Enable()
	stop_btn.Disable()
	stop_btn.SetValue(False)

## START WITH THE CREATION OF THE FRAME
app = wx.App()
app_frame = wx.Frame(None, title='BreakJunction V4: Dilution Fridge Computer')
app_frame.Bind(wx.EVT_CLOSE, QUIT)

## CREATE TWO PANELS, ONE FOR CONTROLS AND ONE FOR PLOTTING
ctrl_panel = wx.Panel(app_frame)
plot_panel = wx.Panel(app_frame)

## FOR THE PLOT PANEL, SET UP THE PLOT
fig = Figure(figsize=(7,10))
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

line1, = ax1.plot([],'-o')
line2, = ax2.plot([],'-rs')

ax1.set_xlabel('Voltage (V)')
ax1.set_ylabel('Current (mA)')

ax2.set_xlabel('Voltage (V)')
ax2.set_ylabel('Conductance')

plot_panel.canvas = FigureCanvasWxAgg(plot_panel, -1, fig)

## FOR THE CONTROL PANEL, SET UP THE STATIC BOXES
apparatus_box = wx.StaticBox(ctrl_panel, wx.ID_ANY, "Apparatus")
settings_box = wx.StaticBox(ctrl_panel, wx.ID_ANY, "Settings")
controls_box = wx.StaticBox(ctrl_panel, wx.ID_ANY, "Controls")
status_box = wx.StaticBox(ctrl_panel, wx.ID_ANY, "Status")

## FOR THE APPARATUS STATICBOX, SET UP INPUT FIELDS
AmpS_label = wx.StaticText(ctrl_panel, wx.ID_ANY, "Amplifier Sensitivity (x10E-)")
AmpS_entry = wx.SpinCtrl(ctrl_panel, wx.ID_ANY, value = '3', size = (80,-1), min = 2, max = 11)

AmpS_sizer = wx.BoxSizer(wx.HORIZONTAL)
AmpS_sizer.Add(AmpS_label, 0, wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
AmpS_sizer.Add(AmpS_entry, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

apparatussizer = wx.BoxSizer(wx.VERTICAL)
apparatussizer.Add(AmpS_sizer, 0, wx.ALIGN_RIGHT, 5)

## FOR THE SETTINGS STATICBOX, SET UP INPUT FIELDS
IncV_label = wx.StaticText(ctrl_panel, wx.ID_ANY, "Increment Voltage (mV)")
IncV_entry = wx.TextCtrl(ctrl_panel, wx.ID_ANY, "1")

DecV_label = wx.StaticText(ctrl_panel, wx.ID_ANY, "Decrement Voltage (mV)")
DecV_entry = wx.TextCtrl(ctrl_panel, wx.ID_ANY, "50")

Sens_label = wx.StaticText(ctrl_panel, wx.ID_ANY, "Drop Sensitivity, 1/x")
Sens_entry = wx.TextCtrl(ctrl_panel, wx.ID_ANY, "350")

FinG_label = wx.StaticText(ctrl_panel, wx.ID_ANY, "Final Conductance (G/G0)")
FinG_entry = wx.TextCtrl(ctrl_panel, wx.ID_ANY, "30")

Samp_label = wx.StaticText(ctrl_panel, wx.ID_ANY, "Samples/Datum")
Samp_entry = wx.SpinCtrl(ctrl_panel, wx.ID_ANY, value = '1', size = (80,-1), min = 1, max = 1000)

Dely_label = wx.StaticText(ctrl_panel, wx.ID_ANY, "Step Delay")
Dely_entry = wx.TextCtrl(ctrl_panel, wx.ID_ANY, "0")

IncV_sizer = wx.BoxSizer(wx.HORIZONTAL)
IncV_sizer.Add(IncV_label, 0, wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
IncV_sizer.Add(IncV_entry, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

DecV_sizer = wx.BoxSizer(wx.HORIZONTAL)
DecV_sizer.Add(DecV_label, 0, wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
DecV_sizer.Add(DecV_entry, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

Sens_sizer = wx.BoxSizer(wx.HORIZONTAL)
Sens_sizer.Add(Sens_label, 0, wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
Sens_sizer.Add(Sens_entry, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

FinG_sizer = wx.BoxSizer(wx.HORIZONTAL)
FinG_sizer.Add(FinG_label, 0, wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
FinG_sizer.Add(FinG_entry, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

Samp_sizer = wx.BoxSizer(wx.HORIZONTAL)
Samp_sizer.Add(Samp_label, 0, wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
Samp_sizer.Add(Samp_entry, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

Dely_sizer = wx.BoxSizer(wx.HORIZONTAL)
Dely_sizer.Add(Dely_label, 0, wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
Dely_sizer.Add(Dely_entry, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

settingssizer = wx.GridSizer(rows = 6, cols = 1, hgap = 5, vgap = 2)
settingssizer.Add(IncV_sizer, 0, wx.ALIGN_RIGHT)
settingssizer.Add(DecV_sizer, 0, wx.ALIGN_RIGHT)
settingssizer.Add(Sens_sizer, 0, wx.ALIGN_RIGHT)
settingssizer.Add(FinG_sizer, 0, wx.ALIGN_RIGHT)
settingssizer.Add(Samp_sizer, 0, wx.ALIGN_RIGHT)
settingssizer.Add(Dely_sizer, 0, wx.ALIGN_RIGHT)

## FOR THE CONTROLS STATICBOX, SET UP BUTTONS
start_btn = wx.Button(ctrl_panel, wx.ID_ANY, "START")
stop_btn = wx.ToggleButton(ctrl_panel, wx.ID_ANY, "END")

start_btn.Bind(wx.EVT_BUTTON, MAIN)
stop_btn.Disable()

controlssizer = wx.BoxSizer(wx.HORIZONTAL)
controlssizer.Add(start_btn, 1, wx.ALL|wx.ALIGN_LEFT|wx.EXPAND, 5)
controlssizer.Add(stop_btn, 1, wx.ALL|wx.ALIGN_RIGHT|wx.EXPAND, 5)


## FOR THE STATUS STATICBOX, SET UP STATIC TEXTS
file_label = wx.StaticText(ctrl_panel, wx.ID_ANY, "Filename:")
elapsed_label = wx.StaticText(ctrl_panel, wx.ID_ANY, "Elapsed:")
file_txt = wx.TextCtrl(ctrl_panel, wx.ID_ANY, "", style=wx.TE_READONLY|wx.TE_CENTER)
elapsed_txt = wx.TextCtrl(ctrl_panel, wx.ID_ANY, "", style=wx.TE_READONLY|wx.TE_CENTER)

statussizer = wx.FlexGridSizer(rows = 2, cols = 2, hgap = 5, vgap = 2)
statussizer.Add(file_label, 0, wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
statussizer.Add(file_txt, 1, wx.ALL|wx.ALIGN_CENTER|wx.EXPAND)
statussizer.Add(elapsed_label, 0, wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
statussizer.Add(elapsed_txt, 1, wx.ALL|wx.ALIGN_CENTER|wx.EXPAND)
statussizer.AddGrowableCol(1,1)

## ARRANGE THE WIDGETS INTO GROUPS
apparatus_box_sizer = wx.StaticBoxSizer(apparatus_box, wx.VERTICAL)
apparatus_box_sizer.Add(apparatussizer, 0, wx.ALL|wx.EXPAND, 5)

settings_box_sizer = wx.StaticBoxSizer(settings_box, wx.VERTICAL)
settings_box_sizer.Add(settingssizer, 0, wx.ALL|wx.EXPAND, 5)

controls_box_sizer = wx.StaticBoxSizer(controls_box, wx.VERTICAL)
controls_box_sizer.Add(controlssizer, 0, wx.ALL|wx.EXPAND, 5)

status_box_sizer = wx.StaticBoxSizer(status_box, wx.VERTICAL)
status_box_sizer.Add(statussizer, 0, wx.ALL|wx.EXPAND, 5)

ctrl_panel_sizer = wx.BoxSizer(wx.VERTICAL)
ctrl_panel_sizer.Add(apparatus_box_sizer,0, wx.ALL|wx.EXPAND, 5)
ctrl_panel_sizer.Add(settings_box_sizer,0, wx.ALL|wx.EXPAND, 5)
ctrl_panel_sizer.Add(controls_box_sizer,0, wx.ALL|wx.EXPAND, 5)
ctrl_panel_sizer.Add(status_box_sizer,0, wx.ALL|wx.EXPAND, 5)
ctrl_panel.SetSizer(ctrl_panel_sizer)

## ARRANGE PLOT ELEMENT INTO SIZER
plotsizer = wx.BoxSizer(wx.HORIZONTAL)
plotsizer.Add(plot_panel.canvas, 0, wx.ALL|wx.EXPAND)
plot_panel.SetSizer(plotsizer)

## ARRANGE PANELS
windowSizer = wx.BoxSizer()
windowSizer.Add(ctrl_panel, 0, wx.ALL|wx.ALIGN_CENTER, 5)
windowSizer.Add(plot_panel, 0, wx.ALL|wx.ALIGN_CENTER, 5)
app_frame.SetSizerAndFit(windowSizer)

app_frame.Show()

##### Initialize the instruments. Calibrate if necessary.
initializeInstruments()

app.MainLoop()

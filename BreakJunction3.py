##========================================================================================================================================>> IMPORT COMMANDS <<=====##

##### A Module for keeping track of time
from time import time, localtime, strftime, sleep

##### Required for try-except-else Error Catching
import sys

##### Required for plot fitting
import numpy

##### A Standard Python Library/Module for GUI
import Tkinter

##### A Module for Plotting and Embedding plots in the GUI
import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

##### Implement the Default mpl Key Bindings
from matplotlib.backend_bases import *
from matplotlib.figure import Figure

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

##### Draw Plots from Data and Update
def plotData(T, V, I, G, steppingSubFig, conductanceSubFig, plotObject):
	
	# Clear Previous Plot Data
	steppingSubFig.clear()
	conductanceSubFig.clear()

	# Provide Labels for stepping subfigure
	steppingSubFig.set_title("Source Stepping")
	steppingSubFig.set_xlabel("Applied Voltage (V)")
	steppingSubFig.set_ylabel("Current Measured (mA)")
	steppingSubFig.grid()

	# Provide Labels for conductace subfigure
	conductanceSubFig.set_title("Conductance")
	conductanceSubFig.set_xlabel("Steps")
	conductanceSubFig.set_ylabel("Conductance (G/G0)")
	conductanceSubFig.grid()

	# Plot data on stepping subfigure
	I_mA = [i*1000 for i in I]
	steppingSubFig.plot(V, I_mA, '-ro')

	# Plot data on conductance subfigure
	G_renormed = [g/7.74809173E-5 for g in G]
	conductanceSubFig.plot(range(len(V)), G_renormed, '-b')

	# Format the stepping subfigure
	#steppingSubFig.autoscale(enable=True, axis='both', tight='True')		<<== Doesn't work on Dil Fridge Computer
	#steppingSubFig.ticklabel_format(style='sci', axis='both', scilimits=(0,0))

	# Format the conductance subfigure
	#conductanceSubFig.autoscale(enable=True, axis='both', tight='True') 		<<== Doesn't work on Dil Fridge Computer
	#conductanceSubFig.ticklabel_format(style='sci', axis='both', scilimits=(0,0))

	# Draw the plots
	plotObject.draw()


##========================================================================================================================>> CORE JUNCTION BREAKING COMMANDS <<=====##

def _START():
	TimeElapsed = []
	Voltage = []
	Current = []
	Conductance = []

	startTime = time.time()
	
	filename = strftime("../BreakJunction3_Data/%Y-%m-%d-%H-%M-%S.csv", time.localtime())
	FileN.set(filename)
	dataFile = open(filename, "a")

	voltageIncStep = float( IncrV.get() )*0.001
	voltageDecStep = float( DecrV.get() )*0.001
	sensitivity = float( Ssvty.get() )	
	finalConductance = float( Final.get() )

	amplifierSensitivity = 10**( -float( AmplS.get() ) )
	samplesPerDatum = int( Sampl.get() )
	stepDelay = float( StepD.get() )/1000

	expLoopIndex = 0
	while active_stat.get():
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
			f = 1-(1/float(lastVoltage*sensitivity))
		except:
			f = float(0)	# Default sensitivity value in case last voltage applied was zero

		if getLast(Current) < f*Iexpected and expLoopIndex > 5 and getLast(Voltage) - voltageDecStep > voltageDecStep:
			k = 0
			while k <= 10 and voltageDecStep < getLast(Voltage) - voltageDecStep:
				elapsed = time.time() - startTime
				TimeElapsed.append(elapsed)
					
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
				current = -(amplifierSensitivity*average_Voltage_reading) 
				Current.append(current)

				conductance = calculateConductance(current,voltage)
				Conductance.append(conductance)

				plotData(TimeElapsed, Voltage, Current, Conductance, steppingSubFig, conductanceSubFig, plotObject)
				root.update()
				time.sleep(stepDelay)

				k = k + 1	

		else:
			elapsed = time.time() - startTime
			TimeElapsed.append(elapsed)

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
			current = -(amplifierSensitivity*average_Voltage_reading) 
			Current.append(current)

			conductance = calculateConductance(current,voltage)
			Conductance.append(conductance)

			plotData(TimeElapsed, Voltage, Current, Conductance, steppingSubFig, conductanceSubFig, plotObject)
			root.update()
			time.sleep(stepDelay)

		if getLast(Conductance)/7.74809173E-5 < finalConductance and expLoopIndex > 100:
			active_stat.set(False)
			print "Conductance reached Final"

		print "%3.0f s, %4.3f V, %4.3f mA, %3.2f G0" %( getLast(TimeElapsed), getLast(Voltage), getLast(Current)*1000.0 , getLast(Conductance)/7.74809173E-5 )
		expLoopIndex = expLoopIndex + 1


	# Save the remaining data files
	while len(Voltage) > 0:
		dataFile.write("%.5e" % TimeElapsed.pop(0) + ",")
		dataFile.write("%.5e" % Voltage.pop(0) + ",")
		dataFile.write("%.5e" % Current.pop(0) + ",")
		dataFile.write("%.5e" % Conductance.pop(0) + "\n")
	
	active_stat.set(True)
	setVoltage(0.0)


def _STOP():
	# Stop the junction breaking process.
	active_stat.set(False)


def _QUIT():
	active_stat.set(False)
	# Deinitialize the Instruments so they can be used again under Spanish Acquisition.
	deinitializeInstruments()

	# Gets rid of the GUI Window
	root.quit()
	root.destroy()


##=========================================================================================================================>> CREATE USER INTERFACE COMMANDS <<=====##

##### Create Window
root = Tkinter.Tk()
root.wm_title("Break Junction V3")

##### This global variable will store the status of the junction breaking process.
active_stat = Tkinter.BooleanVar(root)
active_stat.set(True)

##### Create the figure frame (contains exactly one figure component)
figureFrame = Tkinter.Frame(root)
figureFrame.pack(side = "right", padx = 0, pady = 0, ipadx = 0, ipady = 0)

##### Create the figure component, (with exactly two subfigures)
plotFigure = Figure(figsize=(9,12))

##### Create two subfigures
steppingSubFig = plotFigure.add_subplot(211)
conductanceSubFig = plotFigure.add_subplot(212)

##### Embed Figure into GUI as a child in figureFrame
plotObject = FigureCanvasTkAgg(plotFigure, master = figureFrame)
plotObject.draw()
plotObject.get_tk_widget().pack()

##### Create the control frame
controlFrame = Tkinter.LabelFrame(root, text = "Control Frame")
controlFrame.pack(side = "left", padx = 10, pady = 10, ipadx = 10, ipady = 10)


##### Create "string variables" to tie together user entry elements and experiment setting variables
FileN = Tkinter.StringVar()

IncrV = Tkinter.StringVar()
DecrV = Tkinter.StringVar()
Ssvty = Tkinter.StringVar()
Final = Tkinter.StringVar()

AmplS = Tkinter.StringVar()
Sampl = Tkinter.StringVar()
StepD = Tkinter.StringVar()


##### Set experiment setting defaults
FileN.set("FILE NAME")

IncrV.set("1.0")
DecrV.set("50.0")
Ssvty.set("350.0")
Final.set("50")

AmplS.set("3")
Sampl.set("1")
StepD.set("0")


##### Create user input fields
FileN_entry = Tkinter.Entry(controlFrame, textvariable = FileN)

IncrV_entry = Tkinter.Entry(controlFrame, textvariable = IncrV)
DecrV_entry = Tkinter.Entry(controlFrame, textvariable = DecrV)
Ssvty_entry = Tkinter.Entry(controlFrame, textvariable = Ssvty)
Final_entry = Tkinter.Entry(controlFrame, textvariable = Final)

AmplS_entry = Tkinter.Entry(controlFrame, textvariable = AmplS)
Sampl_entry = Tkinter.Entry(controlFrame, textvariable = Sampl)
StepD_entry = Tkinter.Entry(controlFrame, textvariable = StepD)


##### Arrange buttons in the control frame into a grid
FileN_entry.grid(column = 1, row = 0)

IncrV_entry.grid(column = 1, row = 2)
DecrV_entry.grid(column = 1, row = 3)
Ssvty_entry.grid(column = 1, row = 4)
Final_entry.grid(column = 1, row = 5)

AmplS_entry.grid(column = 1, row = 7)
Sampl_entry.grid(column = 1, row = 8)
StepD_entry.grid(column = 1, row = 9)


##### Create labels for the entry fields
FileN_label = Tkinter.Label(controlFrame, text = "Data saved to file: ", anchor = "e")

IncrV_label = Tkinter.Label(controlFrame, text = "Increase Voltage Step (mV)", anchor = "e")
DecrV_label = Tkinter.Label(controlFrame, text = "Decrease Voltage Step (mV)", anchor = "e")
Ssvty_label = Tkinter.Label(controlFrame, text = "1/x, x = Sensitivity (1/V)", anchor = "e")
Final_label = Tkinter.Label(controlFrame, text = "Final Conductance (G/G0)", anchor = "e")

AmplS_label = Tkinter.Label(controlFrame, text = "Amplifier Sensitivity (10E-... Amps/V)", anchor = "e")
Sampl_label = Tkinter.Label(controlFrame, text = "Samples per Datum", anchor = "e")
StepD_label = Tkinter.Label(controlFrame, text = "Step Delay (ms)", anchor = "e")


##### Arrange labels in the control frame beside the entry fields.
FileN_label.grid(column = 0, row = 0, ipady = 10, ipadx = 10)

IncrV_label.grid(column = 0, row = 2, ipady = 10, ipadx = 10)
DecrV_label.grid(column = 0, row = 3, ipady = 10, ipadx = 10)
Ssvty_label.grid(column = 0, row = 4, ipady = 10, ipadx = 10)
Final_label.grid(column = 0, row = 5, ipady = 10, ipadx = 10)

AmplS_label.grid(column = 0, row = 7, ipady = 10, ipadx = 10)
Sampl_label.grid(column = 0, row = 8, ipady = 10, ipadx = 10)
StepD_label.grid(column = 0, row = 9, ipady = 10, ipadx = 10)


##### Create start button (on click, 'start' will unsuppress commands in experiment loop)
Start_button = Tkinter.Button(controlFrame, text = "START", command = _START)
Start_button.grid(column = 1, row = 11, ipady = 10, ipadx = 5)

##### Create pause button (on click, 'abort' will suppress commands in experiment loop)
Pause_button = Tkinter.Button(controlFrame, text = "STOP", command = _STOP)
Pause_button.grid(column = 1, row = 12, ipady = 10, ipadx = 5)

##### Create quit button (on click, run main program)
Quit_button = Tkinter.Button(controlFrame, text = "QUIT", command = _QUIT)
Quit_button.grid(column = 1, row = 14, ipady = 10, ipadx = 5)

##### Initialize the instruments. Calibrate if necessary.
initializeInstruments()

##### Start the measurement program loop (initially suppressed by stopExpLoop = True)
root.mainloop()

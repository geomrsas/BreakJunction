##### PART 1: IMPORTING NECESSARY COMMANDS AND MODULES

## A Standard Python Library/Module for GUI
import Tkinter

## A Module for Plotting and Embedding plots in the GUI
import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Implement the Default mpl Key Bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

# A Module for keeping track of time
import time

## A Customized Module for updating plots in the GUI
from plotter import *

## A Customized Module to Send and Receive Data/Instructions to Instruments
from acquisition import *

## A Customized Module of short code snippets
from utilities import *

##### PART 2: THE MAIN PROGRAM VARIABLES AND DATA CARRIERS

# The experiment settings
samplesPerDatum = 100		# default = 100
conductanceDropThreshold = 5	# default = 5%
finalConductance = 0.1		# default = 0.1 S
voltageIncStep = 3		# default = 3 V
voltageDecStep = 10		# default = 10 V
amplifierSensitivity = 1E-9	# default = 10E-9 amps/volts

# This will contain the data file information.
# For now, it is a temporary trash file, we will reassign it later.
dataFile = open("FLUSHED.csv", "w")

# This is the start time
startTime = time.time()

# These variables carry the data between functions
T = [0]	# time elapsed since experiment start
V = [0]	# applied voltage across junction
I = [0]	# measured current across junction
G = [0]	# calculated conductances

# The global variable to pause the main experiment loop.
stopExpLoop = True

# The global variable to keep track of the number of steps.
expLoopIndex = 0

##### PART 3.1: ============>>>> THE START PROGRAM <<<<============ !!!!

def start():
	# We must do the following before unsuppressing the expLoop
	
	# 1. Create (if none) or append text to file name provided.
	global dataFile	
	dataFile = open(FileN_StringVar.get() + ".csv", "a")

	# 2. Assign the user inputed experiment settings
	global samplesPerDatum, conductanceDropThreshold, finalConductance
	global voltageIncStep, voltageDecStep, amplifierSensitivity

	voltageIncStep = float( IncrV_StringVar.get() )
	voltageDecStep = float( DecrV_StringVar.get() )
	amplifierSensitivity = float( Ssvty_StringVar.get() )
	samplesPerDatum = float( Sampl_StringVar.get() )
	conductanceDropThreshold = float( DropT_StringVar.get() )
	finalConductance = float( Final_StringVar.get() )

	# Enable experiment loop by setting the global stop to FALSE.
	# We do not need to add a trigger for the experiment loop.
	# The experiment loop has started running in the background.
	# and checks if the stop condition is true or not.
	# Sidenote: global declaration is required to set variable, but not for reading.
	global stopExpLoop
	stopExpLoop = False


##### PART 3.2 ============>>>> THE EXPERIMENT LOOP PROGRAM <<<<============ !!!!

def exploop():
	# call on a global variable
	global expLoopIndex

	# if the main experiment loop is not to be stopped (paused) yet.	
	if not stopExpLoop:
		expLoopIndex +=1
		main()

	# After 1 second, call scanning again (create a recursive loop)
	root.after(1, exploop)


##### PART 3.2 ============>>>> THE MAIN PROGRAM <<<<============ !!!!

def main():
	# Step 0: We will be writing on these global variables
	global T, V, I, G

	# Step 1: Save the last known datum to file
	#         if stored data size exceeds 100 datum
	while len(V)>100:
		dataFile.write("%.5e" % T.pop(0) + ",")
		dataFile.write("%.5e" % V.pop(0) + ",")
		dataFile.write("%.5e" % I.pop(0) + ",")
		dataFile.write("%.5e" % G.pop(0) + "\n")
	
	# Step 2: Time Stamp the coming immediate measurement
	elapsed = time.time() - startTime
	T.extend([elapsed])
	
	m, s = divmod(elapsed, 60)
	h, m = divmod(m, 60)
	elapsed_expression = "%d:%02d:%02d" % (h, m, s)
	Timer_StringVar.set("Elapsed: " + elapsed_expression)

	# Step 3: retrieve the last and next last values of voltage and conductance,
	#	  and calculate the fraction below threshold drop (f)
	lastVoltage = getLast(V)
	nextLastVoltage = getNextLast(V)

	lastConductance = getLast(G)
	nextLastConductance = getNextLast(G)

	f = 1-(float(conductanceDropThreshold)/float(100))

	# Step 4A: IF  the last measured conductance has fallen below the threshold drop,
	#         AND the loop index > 100 (i.e., we have exceeded the initial current and voltage turnup)
	#	  AND the voltage is more than enough to safely draw back the voltage, then...

	if lastConductance < f*nextLastConductance and expLoopIndex > 100 and lastVoltage > voltageDecStep:

		# ... then Step 4A.1 continue to decrease the voltage until the latest voltage is more than twice
		#     the allowed voltage drop OR we have already dropped the voltage at least ten times
		k = 0
		while k >= 10 or (voltageDecStep > lastVoltage - voltageDecStep):
			
			# Step 4A.1.1: Set the next voltage to be a step back
			voltage = lastVoltage - voltageDecStep
			V.extend([voltage])
			setVoltage(voltage)

			# Step 4A.1.2: Measure current through junction
			current = amplifierSensitivity*readVoltage();
			I.extend([current])

			# Step 4A.1.3: Calculate the conductance
			conductance = calculateConductance(current,voltage)
			G.extend([conductance])

			# Step 4A.1.4: Update the plots
			plotData(T, V, I, G, steppingSubFig, conductanceSubFig, plotObject)
	
			# Step 4A.1.5: Go back and check if the voltage has dropped sufficiently or necessarily
			#	    if it has, stop voltage dropping, otherwise, contiue dropping
			k += 1

	# Step 4B: OTHERWISE, either the conductance has not dropped beyond threshold,
	#			 OR we are still in the process of increasing current and voltage turnup
	#			 OR the voltage is too low for a voltage drop (aka fallback), then...
	else:
		
		# then... Step 4.1: Set the next voltage to be a step forward
		voltage = lastVoltage + voltageIncStep
		V.extend([voltage])
		setVoltage(voltage)

		# Step 4.2 Measure current through junction
		current = abs(amplifierSensitivity*readVoltage());
		I.extend([current])

		# Step 4.3: Calculate the conductance
		conductance = calculateConductance(current,voltage)
		G.extend([conductance])

		# Step 4.4: Update the plots
		plotData(T, V, I, G, steppingSubFig, conductanceSubFig, plotObject)
	
	# Step 4C: If the conductance is less than the final conductance AND
	#	    there is more than 100 datapoints (to be well clear of the initial voltage rise)
	if getLast(G) < finalConductance and expLoopIndex > 100:
		pause()





##### PART 3.3 ============>>>> THE ABORT PROGRAM <<<<============ !!!!

def pause():
	# Stop experiment loop by setting the global flag to TRUE.
	global stopExpLoop
	stopExpLoop = True

##### PART 3.3 ============>>>> THE ABORT PROGRAM <<<<============ !!!!

def quit():
	# Pause the experiment
	pause()	

	# Save the remaining data files
	while len(V) > 0:
		dataFile.write("%.5e" % T.pop(0) + ",")
		dataFile.write("%.5e" % V.pop(0) + ",")
		dataFile.write("%.5e" % I.pop(0) + ",")
		dataFile.write("%.5e" % G.pop(0) + "\n")

	# Deinitialize the Instruments
	# So they can be used again under Spanish Acquisition
	deinitializeInstruments()

	# Gets rid of the GUI Window
	root.quit()
	root.destroy()




##### PART 4: BUILDING THE PLOT ELEMENTS

## Create Window
root = Tkinter.Tk()
root.wm_title("Low Temperature Break Junction")

## Create the figure frame (contains exactly one figure component)
figureFrame = Tkinter.Frame(root)
figureFrame.pack(side = "right", padx = 10, pady = 10, ipadx = 10, ipady = 10)

## Create the figure component, (with exactly two subfigures)
plotFigure = Figure(figsize=(7,10), tight_layout = True)

## Create two subfigures
steppingSubFig = plotFigure.add_subplot(211)
conductanceSubFig = plotFigure.add_subplot(212)

## Embed Figure into GUI as a child in figureFrame
plotObject = FigureCanvasTkAgg(plotFigure, master = figureFrame)
plotObject.draw()
plotObject.get_tk_widget().pack()



##### PART 5: BUILDING THE CONTROL ELEMENTS

## Create the control frame
controlFrame = Tkinter.LabelFrame(root, text = "Control Frame")
controlFrame.pack(side = "left", padx = 10, pady = 10, ipadx = 10, ipady = 10)

# Create "string variables" to tie together user entry elements and experiment setting variables
FileN_StringVar = Tkinter.StringVar()
IncrV_StringVar = Tkinter.StringVar()
DecrV_StringVar = Tkinter.StringVar()
Ssvty_StringVar = Tkinter.StringVar()
Sampl_StringVar = Tkinter.StringVar()
DropT_StringVar = Tkinter.StringVar()
Final_StringVar = Tkinter.StringVar()

# Set experiment setting defaults
FileN_StringVar.set("breakjunction_test")
IncrV_StringVar.set("3")
DecrV_StringVar.set("10")
Ssvty_StringVar.set("1e-9")
Sampl_StringVar.set("100")
DropT_StringVar.set("5")
Final_StringVar.set("0.1")

# Create user input fields
FileN_entry = Tkinter.Entry(controlFrame, textvariable = FileN_StringVar)
IncrV_entry = Tkinter.Entry(controlFrame, textvariable = IncrV_StringVar)
DecrV_entry = Tkinter.Entry(controlFrame, textvariable = DecrV_StringVar)
Ssvty_entry = Tkinter.Entry(controlFrame, textvariable = Ssvty_StringVar)
Sampl_entry = Tkinter.Entry(controlFrame, textvariable = Sampl_StringVar)
DropT_entry = Tkinter.Entry(controlFrame, textvariable = DropT_StringVar)
Final_entry = Tkinter.Entry(controlFrame, textvariable = Final_StringVar)

# Arrange buttons in the control frame into a grid
FileN_entry.grid(column = 1, row = 0)
IncrV_entry.grid(column = 1, row = 1)
DecrV_entry.grid(column = 1, row = 2)
Ssvty_entry.grid(column = 1, row = 3)
Sampl_entry.grid(column = 1, row = 4)
DropT_entry.grid(column = 1, row = 5)
Final_entry.grid(column = 1, row = 6)

# Create labels for the entry fields
FileN_label = Tkinter.Label(controlFrame, text = "Save File: Filename (no .extension)", anchor = "e")
IncrV_label = Tkinter.Label(controlFrame, text = "Increase Voltage Step (mV)", anchor = "e")
DecrV_label = Tkinter.Label(controlFrame, text = "Decrease Voltage Step (mV)", anchor = "e")
Ssvty_label = Tkinter.Label(controlFrame, text = "Amplifier Sensitivity (Amps/V)", anchor = "e")
Sampl_label = Tkinter.Label(controlFrame, text = "Samples per Datum", anchor = "e")
DropT_label = Tkinter.Label(controlFrame, text = "Conductance Drop Threshold (%)", anchor = "e")
Final_label = Tkinter.Label(controlFrame, text = "Final Conductance (S)", anchor = "e")

# Arrange labels in the control frame beside the entry fields.
FileN_label.grid(column = 0, row = 0, ipady = 20, ipadx = 10)
IncrV_label.grid(column = 0, row = 1, ipady = 10, ipadx = 10)
DecrV_label.grid(column = 0, row = 2, ipady = 10, ipadx = 10)
Ssvty_label.grid(column = 0, row = 3, ipady = 10, ipadx = 10)
Sampl_label.grid(column = 0, row = 4, ipady = 10, ipadx = 10)
DropT_label.grid(column = 0, row = 5, ipady = 10, ipadx = 10)
Final_label.grid(column = 0, row = 6, ipady = 10, ipadx = 10)

# Create a timer indicator
Timer_StringVar = Tkinter.StringVar()
Timer_StringVar.set("Elapsed: ")
Timer_entry = Tkinter.Message(controlFrame, textvariable = Timer_StringVar, justify = "center")
Timer_entry.grid(column = 0, row = 7, ipady = 10, ipadx = 5)

# Create start button (on click, 'start' will unsuppress commands in experiment loop)
Start_button = Tkinter.Button(controlFrame, text = "START", command = start)
Start_button.grid(column = 1, row = 7, ipady = 10, ipadx = 5)

# Create pause button (on click, 'abort' will suppress commands in experiment loop)
Pause_button = Tkinter.Button(controlFrame, text = "PAUSE", command = pause)
Pause_button.grid(column = 1, row = 8, ipady = 10, ipadx = 5)

# Create quit button (on click, run main program)
Quit_button = Tkinter.Button(controlFrame, text = "SAVE AND QUIT", command = quit)
Quit_button.grid(column = 1, row = 9, ipady = 10, ipadx = 5)

# Initialize the instruments. Calibrate if necessary.
initializeInstruments(vsource_gain = 1, vsource_offset = 0)

# Start the measurement program loop (initially suppressed by stopExpLoop = True)
root.after(1, exploop)
root.mainloop()

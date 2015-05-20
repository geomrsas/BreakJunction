## Draw Plots from Data and Update

def plotData(T, V, I, G, steppingSubFig, conductanceSubFig, plotObject):
	
	# Clear Previous Plot Data
	steppingSubFig.clear()
	conductanceSubFig.clear()

	# Provide Labels for stepping subfigure
	steppingSubFig.set_title("Source Stepping")
	steppingSubFig.set_xlabel("Steps")
	steppingSubFig.set_ylabel("Source Output (V)")
	steppingSubFig.grid()

	# Provide Labels for conductace subfigure
	conductanceSubFig.set_title("Conductance")
	conductanceSubFig.set_xlabel("Time (s)")
	conductanceSubFig.set_ylabel("Conductance (S)")
	conductanceSubFig.grid()

	# Plot data on stepping subfigure
	steppingSubFig.plot(range(len(V)), V, '-ro')

	# Plot data on conductance subfigure
	conductanceSubFig.plot(T, G, '-bs')

	# Format the stepping subfigure
	steppingSubFig.autoscale(enable=True, axis='both', tight='True')
	steppingSubFig.ticklabel_format(style='sci', axis='both', scilimits=(0,0))

	# Format the conductance subfigure
	conductanceSubFig.autoscale(enable=True, axis='both', tight='True')
	conductanceSubFig.ticklabel_format(style='sci', axis='both', scilimits=(0,0))

	# Draw the plots
	plotObject.draw()

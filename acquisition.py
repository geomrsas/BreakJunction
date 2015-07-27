## These brings in device modules from Spanish Acquisition
## for the specific devices: Voltmeter is the Agilent DM34410A and
## the Voltage Source is the IQC Custom 15 Channel Voltage Source.
from spacq.devices.agilent.dm34410a import DM34410A
from spacq.devices.iqc.voltage_source import VoltageSource

## This brings in an object called Quantity (from Spanish Acquisition) 
## required to write voltages to Voltage Source
from spacq.interface.units import Quantity

## Need to import time.
import time

### Define Global (with respect to this module only), Voltmeter
### and Voltage Source Arbitrary Objects (Take heart, they will be overwritten
### in the comming function as the proper devices) 
vsource = object
vmeter = object

### The 6 channel voltage source ports need a bit of calibration before use.
### These global variables will store the gain and offset used.
offset = 0.000133283954193
gain = 1.00158935604

### This must be run before using the other functions
def initializeInstruments(vsource_gain = 1, vsource_offset = 0):
	global vsource, vmeter
	vsource = VoltageSource(usb_resource = 'USB0::0x3923::0x7166::01456739::RAW')
	vmeter = DM34410A(gpib_board = 0, gpib_pad = 21, gpib_sad = 0)

### At the end of the program this module is used, one should disconnect the instruments
### so that they can be used in another application later
def deinitializeInstruments():
	setVoltage(0)
	global vsource, vmeter
	vsource.close()
	vmeter.close()

### Get reading from the Voltage Meter (DOES NOT INCLUDE SCALING FROM AMPLIFIER)
def readVoltage():
	reading = vmeter.resources['reading'].value.value 	## The value is given in volts.
	time.sleep(0.05)
	return float(reading)

### Set Voltage on the Voltage Source (in Volts please)
def setVoltage(voltage):
	v = offset + gain * float(voltage) 			# Just in case you entered some integer
	vsource.ports[0].voltage = Quantity(voltage,'V')
	time.sleep(0.05)

### Attach a direct line from the Voltage Source Port to the Voltmeter before running this.
def calibrate():
	setVoltage(0)
	vmean = []
	for i in range(100):
		vmean.append(readVoltage())
	print( -float(sum(vmean))/float(len(vmean)) )
	
	setVoltage(0.1)
	vmean = []
	for i in range(100):
		vmean.append(readVoltage())
	print( float(0.1)/float(readVoltage()) )

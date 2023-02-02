#!/usr/bin/python2
# SR-110U / SHARI programmer by KC9MNE 2/1/2023 (modified from original script by N8AR who did a really great job!)
#Version 1.00
#Created by modifying 
#   A Simple SerialProgrammer for the 818 VHF/UHF Modules
#   by w0anm which was created from examples on the web
#   This code was originally,
#   $Id: 818-prog 12 2014-12-27 18:27:47Z w0anm $

#Change Log

#Version 1.08XU - Forked from 1.08X code version by N8AR modified to work with junk China SR-110U chipset with power selection

import time
import serial
import sys
import os.path
 
#constants
flag = '0'

if len(sys.argv) > 1:
	flag = str(sys.argv[1])

tx_ctcss = '';
rx_ctcss = '';
tx_dcs = '';
rx_dcs = '';
CTCSS_Reverse_Burst = '0';
prog_ver = '1.08xU'

#CTCSS tone to code dictionary
codelookup = {
	"0": "0000", 
	"67.0": "0001",
	"71.0": "0002",
	"74.4": "0003",
	"77.0": "0004",
	"79.7": "0005",
	"82.5": "0006",
	"85.4": "0007",
	"88.5": "0008",
	"91.5": "0009",
	"94.8": "0010",
	"97.4": "0011",
	"100.0": "0012",
	"103.5": "0013",
	"107.2": "0014",
	"110.9": "0015",
	"114.8": "0016",
	"118.8": "0017",
	"123.0": "0018",
	"127.3": "0019",
	"131.8": "0020",
	"136.5": "0021",
	"141.3": "0022",
	"146.2": "0023",
	"151.4": "0024",
	"156.7": "0025",
	"162.2": "0026",
	"167.9": "0027",
	"173.8": "0028",
	"179.9": "0029",
	"186.2": "0030",
	"192.8": "0031",
	"203.5": "0032",
	"210.7": "0033",
	"218.1": "0034",
	"225.7": "0035",
	"233.6": "0036",
	"241.8": "0037",
	"250.3": "0038"
}
# DCS codes.
dcs_codes = ["023", "025", "026", "031", "032", "036", "043", "047", "051", "053",
	"054", "065", "071", "072", "073", "074", "114", "115", "116", "122",
	"125", "131", "132", "134", "143", "145", "152", "155", "156", "162",
	"165", "172", "174", "205", "212", "223", "225", "226", "243", "244",
	"245", "246", "251", "252", "255", "261", "263", "265", "266", "271", 
	"274", "306", "311", "315", "325", "331", "332", "343", "346", "351",
	"356", "364", "365", "371", "411", "412", "413", "423", "431", "432",
	"445", "446", "452", "454", "455", "462", "464", "465", "466", "503",
	"506", "516", "523", "526", "532", "546", "565", "606", "612", "624",
	"627", "631", "632", "654", "662", "664", "703", "712", "723", "731",
	"732", "734", "743", "754"]

# configure the serial connections (the parameters differs on the device 
# you are connecting to).  ttyUSB0 is used for SHARI PiXX and SR110U
# ttyAMA0 is used for SHARI PiHat.  Selection is automatic.
try:
	ser = serial.Serial(
	port='/dev/ttyUSB0',
	baudrate=9600,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1
	)
except: 
	ser = serial.Serial(
	port='/dev/ttyAMA0',
	baudrate=9600,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1
	)

# Splash screen
print ('------------------------------------------------------')
print ('\r\n')
print ('SR110U-Prog, Version ' + prog_ver + '\r\n')
print ('Programing Modules Based on SR-110U Radio chip aka SR_FRS_1WU ect \r\n')
print ('Programming Device name:')
print ('      ' + ser.portstr)       # show which port was really used
print ('')
print ('------------------------------------------------------')
print ('')

# Retrieve the last SR110U configuration done by this program and print it.

file_exists = os.path.exists('/root/SR110U.log')

if file_exists:
	a_file = open("/root/SR110U.log")
	lines = a_file.readlines()
	for line in lines:
		line = line.rstrip('\r\n')
		print(line)
	a_file.close()
else:
	print ('No previous programming data available.\r\n')

# Check for serial communications with the SR110U
print ('Testing serial communications')
ser.write("AT+DMOCONNECT" + "\r\n")
time.sleep(2.00)
raw_serial = ser.readline()
response = raw_serial[:-2]
if response == "+DMOCONNECT:0": 
	print ('Serial communications with the SR110U module are OK')
	print ("")
else:
	print("No serial communication with the SR110U module")
	exit()
 # Read and print firmware version.  
        print ('Reading SR110U firmware version')
        ser.write("AT+DMOVERQ" + "\r\n")
        time.sleep(1.00)
        raw_serial = ser.readline()
        firmware = raw_serial[:-2]
        print (" Firmware Version: " + firmware + "\r\n")

# Ask what we are programming (1-SHARI PiXX 2-SHARI PiHat  3-SA818 Module)
# If PiXX or PiHat set the channel spacing to wide
while True:
	try:
		print('What are you programming?')
		Device=raw_input("Enter 1,2 or 3 where SHARI PiXX=1, SHARI PiHat=2, SA818 Module=3: ")
		if int(Device) not in [1,2,3]:
			raise ValueError()
		break;
	except ValueError:
		print("	Sorry, you must enter either a 1, 2 or 3\r\n")
		continue;  
	finally:
		if Device == '1':
			print('\r\n	Programming a SHARI PiXX')
			print('	Wide channel spacing')
			print('')
			Spacing = "1"
		elif Device == '2':
			print('\r\n	Programming a SHARI PiHat')
			print('	Wide channel spacing')
			print('')
			Spacing = "1"        
	break
	
# Programming a generic SA818 module so we have to enter a channel spacing	
while True:
	if Device == '3':
		try:
			print('	\r\nProgramming a generic SA818 module')
			Spacing=raw_input('Enter Channel Spacing (Narrow=0 or Wide=1): ') 
			if int(Spacing) not in [0,1]:
				raise ValueError()
			break;
		except ValueError:
			print("	Sorry, you must enter eiher a 0 or a 1")
			continue
		finally:
			if Spacing == "0":
				print('\r\n	Programming an SA818 module')
				print('	Narrow channel spacing')
				print('')
			elif Spacing == "1":
				print('\r\n	Programming an SA818 module')
				print('	Wide channel spacing')
				print('')
		break
	break

# Ask which band, UHF or VHF	
while True:
	try:
		Band=raw_input('Enter band (VHF=1, UHF=2): ')
		if int(Band) not in [1,2]:
			raise ValueError()
		break; 
	except ValueError:
		print("	Sorry, you must enter either a 1 or a 2\r\n")
		continue  
	finally:
		if str(Band) == '1':
			print("	You chose VHF")
			print('')
		if str(Band) == '2':
			print("	You chose UHF")
			print('')
	break

# Ask for transmit frequency.  Make sure it is in 2m or 70 cm ham band. Correct input format errors
while True:
	try:
		FreqTx=str(raw_input('Enter transmit frequency in MHz (xxx.xxxx): '))
		if Band == '1':
			freq=FreqTx.split('.');
			if int(freq[0]) < 144 or int(freq[0]) > 148:
				raise ValueError();
				break;
		elif Band == '2':
			freq=FreqTx.split(".");
			if int(freq[0]) < 420 or int(freq[0]) > 450:
				raise ValueError();
			break;
	except ValueError as err:
			if Band == '1':
				print("The Tx frequency must be entered as (xxx.xxxx) and must be between 144.0000 and 148.0000.\r\n")
			elif Band == '2':
				print("The Tx frequency must be entered as (xxx.xxxx) and must be between 420.0000 and 450.0000.\r\n")
			continue
	finally:
		if len(freq) < 2:
			freq.append('0000');
		elif len(freq[1]) == 1:
			freq[1] = freq[1] + '000';
		elif len(freq[1]) == 2:
			freq[1] = freq[1] + '00';
		elif len(freq[1]) == 3:
			freq[1] = freq[1] + '0';    
		FreqTx = freq[0] + "." + freq[1];
	break

print('	The transmit frequency is ' + FreqTx + ' MHz\r\n');

# Ask for receive frequency.  Make sure it is in 2m or 70 cm ham band. Correct input format errors
while True:
	try:
		FreqRx=str(raw_input('Enter receive frequency in MHz(xxx.xxxx): '))
		if Band == '1':
			freq=FreqRx.split(".");
			if int(freq[0]) < 144 or int(freq[0]) > 148:
				raise ValueError();
			break;
		elif Band == '2':
			freq=FreqRx.split(".");
			if int(freq[0]) < 420 or int(freq[0]) > 450:
				raise ValueError();
				break;
	except ValueError as err:
			if Band == '1':
				print("The Rx frequency must be entered as (xxx.xxxx) and must be between 144.0000 and 148.0000.\r\n")
			elif Band == '2':
				print("The Rx frequency must be entered as (xxx.xxxx) and must be between 420.0000 and 450.0000.\r\n")
			continue
	finally:
		if len(freq) < 2:
			#print(len(freq));
			freq.append('0000');
		elif len(freq[1]) == 1:
			freq[1] = freq[1] + "000";
		elif len(freq[1]) == 2:
			freq[1] = freq[1] + "00";
		elif len(freq[1]) == 3:
			freq[1] = freq[1] + "0";    
		FreqRx = freq[0] + "." + freq[1];
	break

print('	The receive frequency is ' + FreqRx + ' MHz\r\n');

#Ask if using subaudible tone
while True:
	try:
		audtone=str(raw_input('Do you want to use a sub audible tone? (0 = No, 1 = CTCSS, 2= DCS): '))
		if int(audtone) not in [0,1,2]:
			raise ValueError()
		break; 
	except ValueError:
		print("	Sorry, you must enter either 0, 1 or 2\r\n")
		continue  
	finally:
		if audtone == '0':
			print("	You chose No SubAudible Tone")
			print('')
			tx_ctcss = "0000" #The string '0000' means no sub-audible tone
			rx_ctcss = "0000" #for transmit and/or receive
		if audtone == '1':
			print("	You chose CTCSS")
			print('')
		if audtone == '2':
			print("	You chose DCS")
			print('')
	break

while True:
	try:
		if not audtone == '1':
			break
		txctcss=str(raw_input('Enter Tx CTCSS Frequency in Hz(xxx.x): '))
		if txctcss in codelookup:
			print('	You entered ' + txctcss + ' Hz') 
		else:
			raise ValueError()
	except ValueError:
		print("	Tx CTCSS frequency is incorrect, please re-enter\r\n")
		continue
	else:
		if not audtone == '1':
			break
		tx_ctcss = str(codelookup.get(txctcss))
		print('	The Tx CTCSS code is ' + tx_ctcss)
		print('')
		break

while True:
	try:
		if not audtone == '1':
			break
		rxctcss=str(raw_input('Enter Rx CTCSS Frequency in Hz(xxx.x): '))
		if rxctcss in codelookup:
			print('	You entered ' + rxctcss + ' Hz') 
		else:
			raise ValueError()
	except ValueError:
		print("	Rx CTCSS frequency is incorrect, please re-enter\r\n")
		continue
	else:
		if not audtone == '1':
			break
		rx_ctcss = str(codelookup.get(rxctcss))
		print('	The Rx CTCSS code is ' + rx_ctcss)
		print('')
	break

#A CTCSS frequency has been entered. Ask about reverse burst
while True:
	try:
		if not audtone == '1':
			break;
		CTCSS_RB=str(raw_input('Enable Reverse Burst (y/[n]): ')).lower()
		if CTCSS_RB == "":
			CTCSS_RB="n"
		if (CTCSS_RB != 'y') and (CTCSS_RB != 'n'):
				raise ValueError();
	except ValueError as err:
		print("	You must enter y or n\r\n")
		continue
	else:
		if audtone == '1':
			if CTCSS_RB == 'y':
				print('	Reverse burst is enabled\r\n')
				CTCSS_Reverse_Burst = '1'
			else:
				print('	Reverse burst is not enabled\r\n')
				print
				TCSS_Reverse_Burst = '0'
	break

while True:
	try:
		if not audtone == '2':
			break
		ans=str(raw_input('Would you like a list of valid DCS codes? (y/[n]): ')).lower()
		if ans == "y":
			print('')
			print('A valid DCS code is three digits as shown in the following table')
			print('followed by an N (normal) or I (inverted)')
			print('')
			i = 0;
			for a in dcs_codes:
				i=i+1;
				if i == 8:
					sys.stdout.write(a + ' ');
					print("");
					i = 0;
				else:
					sys.stdout.write(a + ' ');

		txdcs=str(raw_input('\r\nEnter Tx DCS Code (xxxx): ')).upper()
		if len(txdcs) < 4:
			raise ValueError()
		if txdcs[0:3] not in dcs_codes:
			raise ValueError()
		if txdcs[3] not in ["I", "N"]:
			raise ValueError()
	except ValueError:
		print('	Code is incorrect')
		print('	Please re-enter as three digits followed by an N or I')
		continue
	finally:
		if not audtone == '2':
			break
		print('	You entered ' + txdcs + '\r\n')
		tx_dcs = txdcs;
	break
	
while True:
	try:
		if not audtone == '2':
			break
		rxdcs=str(raw_input('Enter Rx DCS Code (xxxx): ')).upper()
		if len(rxdcs) < 4:
			raise ValueError()
		if rxdcs[0:3] not in dcs_codes:
			raise ValueError()
		if rxdcs[3] not in ["I", "N"]:
			raise ValueError()
	except ValueError:
		print('	Code is incorrect')
		print('	Please re-enter as three digits followed by an N or I')
		continue
	finally:
		if not audtone == '2':
			break
		print('	You entered ' + rxdcs + '\r\n')
		rx_dcs = rxdcs;
	break

#A CDCSS frequency has been entered. Ask about reverse burst
while True:
	try:
		if not audtone == '2':
			break;
		CTCSS_RB=str(raw_input('Enable Reverse Burst (y/[n]): ')).lower()
		if CTCSS_RB == "":
			CTCSS_RB="n"
		if (CTCSS_RB != 'y') and (CTCSS_RB != 'n'):
				raise ValueError();
	except ValueError as err:
		print("	You must enter y or n\r\n")
		continue
	else:
		if audtone == '2':
			if CTCSS_RB == 'y':
				print('	Reverse burst is enabled\r\n')
				CTCSS_Reverse_Burst = '1'
			else:
				print('	Reverse burst is not enabled\r\n')
				print
				CTSS_Reverse_Burst = '0'
	break

# Enter squelch value (1-8)
while True:
	try:
		sq=raw_input('Enter Squelch Value (1-8): ')
		if int(sq) < 1 or int(sq) > 8:    
			raise ValueError();
	except ValueError:
		print("	Squelch must be an integer between 1 and 8\r\n")
		continue
	finally:
		squelch = str(sq)
	break
print("	Squelch is set to " + squelch)
print('')

# Enter volume value (1-8)
while True:
	try:
		vol=raw_input('Enter Volume (0-8): ')
		if int(vol) < 1 or int(vol) > 8:
			raise ValueError();
	except ValueError:
		print("	Volume must be an integer between 1 and 8\r\n")
		continue
	finally:
		Volume = str(vol)
	break
print("	Volume is set to " + Volume)
print('')

# Enter TX Power value (0-1)
while True:
	try:
		txpwr=raw_input('Enter TX Power Mode 0=High 1=Low (0,1): ')
		if int(vol) < 1:
			raise ValueError();
	except ValueError:
		print("	Volume must be an integer between 0 and 1\r\n")
		continue
	finally:
		xmitpwr = str(txpwr)
	break
print("	TX power is set to " + xmitpwr)
print('')

# Ask about pre-emphasis
while True:
		try:
			PreEmphasis=str(raw_input('Enable Pre/De-Emphasis (y/[n]): ')).lower()
			if PreEmphasis == "":
				PreEmphasis="n"
			if (PreEmphasis != 'y') and (PreEmphasis != 'n'):
				raise ValueError();
		except ValueError as err:
			print("Must enter Y or N")
			continue
		finally:
			if PreEmphasis == 'y':
				print('	Pre/De-emphasis is enabled')
				print
			else:
				print('	Pre/De-emphasis is not enabled')
				print
		break

# Ask about high pass filter
while True:
		try:
			HighPass=str(raw_input('Enable High Pass Filter (y/[n]): ')).lower()
			if HighPass == "":
				HighPass="n"
			if HighPass != "y" and HighPass != "n":
				raise ValueError();
		except ValueError as err:
			print("Must enter Y or N")
			continue
		finally:
			if HighPass == 'y':
				print('	High pass filter is enabled')
				print
			else:
				print('	High pass filter is not enabled')
				print
		break

# Ask about low pass filter
while True:
		try:
			LowPass=str(raw_input('Enable Low Pass Filter (y/[n]): ')).lower()
			if LowPass == "":
				LowPass="n"
			if LowPass != "y" and LowPass != "n":
				raise ValueError();
		except ValueError as err:
			print("Must enter Y or N")
			continue
		finally:
			if LowPass == 'y':
				print('	Low pass filter is enabled')
				print
			else:
				print('	Low pass filter is not enabled')
				print
		break
#
#
#
print ('')
print ('Verify:')
print ('------------------------------------------------------')
print ('     Channel Spacing: ' + Spacing + ' ')
print ('        Tx Frequency: ' + FreqTx + ' ')
print ('        Rx Frequency: ' + FreqRx + ' ')
if audtone == '0':
	print ('       Tx CTCSS code: 0000')
	print ('       Rx CTCSS code: 0000')	
if audtone == '1':
	print ('       Tx CTCSS code: ' + tx_ctcss + ' Frequency: ' + txctcss + ' Hz')
	print ('       Rx CTCSS code: ' + rx_ctcss + ' Frequency: ' + rxctcss + ' Hz')
	print (' CTCSS Reverse Burst: ' + CTCSS_RB + ' ')
if audtone == '2':
	print ('         Tx DCS code: ' + tx_dcs + ' ')
	print ('         Rx DCS code: ' + rx_dcs + ' ')
	print (' CTCSS Reverse Burst: ' + CTCSS_RB + ' ')
print ('       Squelch Value: ' + squelch + ' ')
print ('        Volume Value: ' + Volume + ' ')
print (' PreEmphasis Enabled: ' + PreEmphasis + ' ')
print ('   High Pass Enabled: ' + HighPass + ' ')
print ('    Low Pass Enabled: ' + LowPass + ' ')

print ('------------------------------------------------------')

# Ask if the values are correct and whether to program the unit
Answer=str(raw_input('Is this correct ([y]/n, or a to abort) ?')).lower().strip()
if Answer == "":
	Answer = "y";

if Answer == "y":
	print('')

if Answer == "a" or Answer == "n":
	print('')
	print('Press the <UP-ARROW> and <enter> on your keyboard to re-run the program')
	print('')
	exit();
	exit

# Print configuration to file N4IRS
# Write a log of the configuration to /root/SA818.log
with open('/root/SA818.log', 'w') as f:
	f.write ('\n')
	f.write ('Last values programed to SA818:\n')
	f.write ('------------------------------------------------------\n')
	f.write ('     Channel Spacing: ' + Spacing + ' \n')
	f.write ('        Tx Frequency: ' + FreqTx + ' \n')
	f.write ('        Rx Frequency: ' + FreqRx + ' \n')
	if audtone == '0':
	        f.write ('       Tx CTCSS code: 0000\n')
	        f.write ('       Rx CTCSS code: 0000\n')
	if audtone == '1':
	        f.write ('       Tx CTCSS code: ' + tx_ctcss + ' Frequency: ' + txctcss + ' Hz\n')
	        f.write ('       Rx CTCSS code: ' + rx_ctcss + ' Frequency: ' + rxctcss + ' Hz\n')
	        f.write (' CTCSS Reverse Burst: ' + CTCSS_RB + ' \n')
	if audtone == '2':
	        f.write ('         Tx DCS code: ' + tx_dcs + ' \n')
	        f.write ('         Rx DCS code: ' + rx_dcs + ' \n')
	        f.write (' CTCSS Reverse Burst: ' + CTCSS_RB + ' \n')
	f.write ('       Squelch Value: ' + squelch + ' \n')
	f.write ('        Volume Value: ' + Volume + ' \n')
	f.write (' PreEmphasis Enabled: ' + PreEmphasis + ' \n')
	f.write ('   High Pass Enabled: ' + HighPass + ' \n')
	f.write ('    Low Pass Enabled: ' + LowPass + ' \n')

	f.write ('------------------------------------------------------\n')

# Read and print firmware version.  Invoke this by using SA818-prog -v to start program
if flag == '-v':
	print ('Reading firmware version')
	ser.write("AT+DMOVERQ" + "\r\n")
	time.sleep(1.00)
	raw_serial = ser.readline()
	response = raw_serial[:-2]
	print (" Firmware Version " + response + "\r\n")
	
# Write the data to the SA818 module

# Set Freq/Group
# Example of the command:
#     ser.write("AT+DMOSETGROUP=1,446.0500,446.0500,0020,4,0020\r\n")
print ('Sending Frequency, Sub Audible Tone, and Squelch Information...')
if audtone == '0' or audtone == '1':
	ser.write("AT+DMOSETGROUP=" + Spacing + "," + FreqTx + "," + FreqRx + "," + tx_ctcss + "," + squelch + "," + rx_ctcss + "\r\n")
	time.sleep(1.00)
if audtone == '2':
	ser.write("AT+DMOSETGROUP=" + Spacing + "," + FreqTx + "," + FreqRx + "," + tx_dcs + "," + squelch + "," + rx_dcs + "\r\n")
	time.sleep(1.00)
raw_serial = ser.readline()
response = raw_serial[:-2]
if response == "+DMOSETGROUP:0": 
	print ('Frequency, Sub Audible Tone, and Squelch information correct')
	print ("")
	print ("Command Sent Was: ")
	print ("        AT+DMOSETGROUP=1," + FreqTx + "," + FreqRx + "," + tx_ctcss + "," + squelch + "," + rx_ctcss + "\r\n")
else:
	print("Frequency, Sub Audible Tone, and/or Squelch information were incorrect")
	print ("Command Sent:")
	print ("        AT+DMOSETGROUP=1," + FreqTx + "," + FreqRx + "," + tx_ctcss + "," + squelch + "," + rx_ctcss + "\r\n")
	print (" The Error was: " + response + "\r\n")
	exit()

# Set Volume

print ("Setting Volume - " + Volume + " ")
ser.write("AT+DMOSETVOLUME=" + Volume + "\r\n")
time.sleep(1.00)

#evaluate response
raw_serial = ser.readline()
response = raw_serial[:-2]

# Bad response --> +DMOSETVOLUME:1
if response == '+DMOSETVOLUME:1':
	print ("    Error, invalid information (" + response + ")...")
	print (" Command Sent:")
	print ("    AT+DMOSETVOLUME=" + Volume + "\r\n")
	exit()

# Set CTCSS Reverse Burst

print ("Setting Reverse Burst")
ser.write("AT+SETTAIL=" + CTCSS_Reverse_Burst + "\r\n")
time.sleep(1.00)

#evaluate response
# Can not evaluate because an error in NiceRF code always returns a '0'

# Set Filters:
# convert filters values, 0 is enable, and 1 is disable

if PreEmphasis == "n":
	PreEmpFilter='1'
else:
	PreEmpFilter='0'

if HighPass == "n":
	HPass='1'
else:
	HPass='0'

if LowPass == "n":
	LPass='1'
else:
	LPass='0'

print ('Setting Filters\r\n')
ser.write("AT+SETFILTER=" + PreEmpFilter + "," + HPass + "," + LPass + "\r\n")
time.sleep(1.00)

#evaluate response
raw_serial = ser.readline()
response = raw_serial[:-2]

# Bad response --> +DMOSETFILTER:1
if response == '+DMOSETFILTER:1':
	print ("    Error, invalid information (" + response + ")...")
	print (" Command Sent:")
	print ("    AT+SETFILTER=" + PreEmpFilter + "," + HPass + "," + LPass + "\r\n")
	exit()
	
print('Programming Successful\r\n')
print('Configuration log written to /root/SA818.log\r\n')	


from datetime import datetime
import pyrebase
import os,sys,datetime, time, subprocess

def Usage(script_name):
	sys.stdout.write("Usage:python3 "+ script_name + " <-Time Unit(H,M,S)>" + " <Duration>\n")
	sys.exit()


##DB constants
firebaseConfig={
##Paste config here
}
firebase= pyrebase.initialize_app(firebaseConfig)
db= firebase.database()



##Program constants
hourToke= '-H'
minuteToke= '-M'
secondToke= '-S'
secs_in_Hour= 3600
secs_in_Min= 60
shell_scan_args = ['bluetoothctl' , 'scan', 'on']
shell_ping_args = ['bluetoothctl', 'devices' ]
found_Devices= {}


##For testing purposes will remove the current result file from directory.
##refresh_Out= 'rm results.txt'
##os.system(refresh_Out)

##file_Out= open('results.txt', 'w')
##input_writer= subprocess.Popen(shell_cmd_args, stdout= file_Out)
##Scan  = subprocess.run(shell_scan_args)
##converts user defined time to seconds if another unit was specified.

def convertTime(unitToke, Duration):
	if unitToke == hourToke:
		return Duration * secs_in_Hour
	elif unitToke == minuteToke:
		return Duration * secs_in_Min
	else:
		Usage(sys.argv[0])
		return 0


def Discovery(unitTime, Duration):
	if unitTime == secondToke:
		discoveryLength= Duration
	else:
		discoveryLength= convertTime(unitTime, Duration)
	start_time= time.time()
	while(time.time() < start_time + discoveryLength):
		try: ##scan for new devices, subprocess must be killed in order to gather results
			Scan= subprocess.run(shell_scan_args, timeout= 2)
			Scan.system("scan off")
		except subprocess.TimeoutExpired:
			sys.stdout.write("Scan Complete\n") ##Notifies that scan is complete and results are ready to be gathered.
		Ping = subprocess.check_output(shell_ping_args) ##Ping to gather results from scanning. 
		Ping= Ping.decode("utf-8")
		##print(Ping + "this is ping")
		for device in Ping.splitlines():
			deviceI = str(device[6:24])
			currTime = str(datetime.datetime.now())
			if deviceI not in found_Devices.keys(): ##new device, append to dictionary and data file
				##sys.stdout.write(device) ##[6:24] =  device macAddress
				##file_Out.write(deviceI + "\n")
				found_Devices[deviceI] = []
				found_Devices[deviceI].append(currTime)
				db.child(deviceI).set(currTime)
			else:
				try:
					found_Devices[deviceI].append(currTime) ##adds time stamp to track the duration of each device in proximity.
					db.child(deviceI).set(found_Devices[deviceI])
				except KeyError as e:
					db.child("ERROR").set(currTime)
					os.system("python footTraffic.py -H 1")

		time.sleep(240) ##Alleviates redundant pinging from device.  
##	file_Out.close()
	for device in found_Devices.keys(): ##prints each unique device found after scan is complete
		for timestamps in found_Devices[device]:
			print(device +" : " + str(timestamps))
	db.child("FINISHED").set([str(datetime.datetime.now()),len(found_Devices.keys())])

if __name__ == "__main__":
	argc= len(sys.argv)
	if argc != 3:  ##All args must be present, if not exit program 
		Usage(sys.argv[0])
	else:
		Discovery(sys.argv[1], float(sys.argv[2]))
		

















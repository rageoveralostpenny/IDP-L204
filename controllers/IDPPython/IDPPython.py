from controller import Robot, Motor, DistanceSensor, LightSensor, GPS, Compass, Receiver, Emitter			
import math			
import struct			
TIME_STEP = 24 #adjusted to give sensor values at the appropriate interval			
MAX_SPEED = 7.5	# based on realistic motor performance		
# create a robot			
robot = Robot() 			
# get devices			
us_right = robot.getDevice("us_right")			
us_left = robot.getDevice("us_left")			
ir = robot.getDevice("ir")			
light_sensor = robot.getDevice("TEPT4400") #this one is angled forwards		
light_sensor_l = robot.getDevice("TEPT4400_left") #this one is angled slightly inwards		
light_sensor_r = robot.getDevice("TEPT4400_right") #this one is straight down			
motor_left = robot.getDevice("Wheel_L")			
motor_right = robot.getDevice("Wheel_R")			
arm_left = robot.getDevice("Arm_L")			
arm_right = robot.getDevice("Arm_R")			
compass = robot.getDevice("compass")			
gps = robot.getDevice("gps")			
receiver = robot.getDevice("receiver")			
emitter = robot.getDevice("emitter")

#enable devices			
us_right.enable(TIME_STEP)			
us_left.enable(TIME_STEP)			
ir.enable(TIME_STEP)			
light_sensor.enable(TIME_STEP)			
light_sensor_l.enable(TIME_STEP)		
light_sensor_r.enable(TIME_STEP)		
compass.enable(TIME_STEP)			
gps.enable(TIME_STEP)			
receiver.enable(TIME_STEP)	
    
#SEND COORDINATES OF BLOCKS OF WRONG COLOUR TO OTHER BOT
def sendFinished():
    message = struct.pack("i",1)		
    emitter.send(message)

#RECEIVES COORDINATES FOR ONE BLOCK
def receivingData():		
    if receiver.getQueueLength() != 0:
        message=receiver.getData()	
        otherRobotFinished = True
        receiver.nextPacket()  

def testIfTargetTheSame(otherRobotTarget,thisRobotTarget):	
    if abs(otherRobotTarget[0] - thisRobotTarget[0]) < 0.05 and abs(otherRobotTarget[1] - thisRobotTarget[1]) < 0.05:	
        sameTarget = True	
    else:	
        sameTarget = False	
    return sameTarget	
    	
#====================================MOTION FUNCTIONS=================================	#
#position set to infinity so motor speed in controlled, not posiiton
def move_forwards():			
    motor_left.setPosition(float('inf'))			
    motor_right.setPosition(float('inf'))			
    motor_left.setVelocity(MAX_SPEED)			
    motor_right.setVelocity(MAX_SPEED)			
def open_arms():			
    arm_left.setPosition(0.35)			
    arm_right.setPosition(-0.35)	
def open_arms_wide():			
    arm_left.setPosition(0.5)			
    arm_right.setPosition(-0.5)			
def close_arms():			
    arm_left.setPosition(-0.22) 			
    arm_right.setPosition(0.22)   			
def rotate_ACW():	# rotation is slow so enough sensor reading can be taken while it rotates		
    motor_left.setPosition(float('inf'))			
    motor_right.setPosition(float('inf'))			
    motor_left.setVelocity(-0.25 * MAX_SPEED)			
    motor_right.setVelocity(0.25 * MAX_SPEED)			
def rotate_CW():			
    motor_left.setPosition(float('inf'))			
    motor_right.setPosition(float('inf'))			
    motor_left.setVelocity(0.25 * MAX_SPEED)			
    motor_right.setVelocity(-0.25 * MAX_SPEED)			
def shuffle_back(): # robot moves backwards a short distance			
    motor_left.setPosition(float('inf'))			
    motor_right.setPosition(float('inf'))			
    motor_left.setVelocity(-MAX_SPEED)			
    motor_right.setVelocity(-MAX_SPEED)					
    i=0			
    while robot.step(TIME_STEP) != -1:			
      i += 1			
      if i==100: # stops moving after 100 time steps			
        motor_left.setVelocity(0)			
        motor_right.setVelocity(0)			
        break				
def shuffle_back_short(): #same as shuffle_back but half the distace		
    motor_left.setPosition(float('inf'))			
    motor_right.setPosition(float('inf'))			
    motor_left.setVelocity(-MAX_SPEED)			
    motor_right.setVelocity(-MAX_SPEED)					
    i=0			
    while robot.step(TIME_STEP) != -1:			
      i += 1			
      if i==50:			
        motor_left.setVelocity(0)			
        motor_right.setVelocity(0)			
        break
def shuffle_back_shortest(): 
#prevents the green robot from backing into
#the red starting square in a very specific case		
    motor_left.setPosition(float('inf'))			
    motor_right.setPosition(float('inf'))			
    motor_left.setVelocity(-MAX_SPEED)			
    motor_right.setVelocity(-MAX_SPEED)					
    i=0			
    while robot.step(TIME_STEP) != -1:			
      i += 1			
      if i==120:			
        motor_left.setVelocity(0)			
        motor_right.setVelocity(0)			
        break		
def wait(): #wait 20 time steps
    wait = 0
    while robot.step(TIME_STEP) != -1 and wait<20:
        wait += 1 
#============================READING SENSOR VALUES====================================        				
def getColour():		
    #this function only checks if the sensor is returning a high value			
    #The colour of the LED will depend on the robot, b/c different filters are applied			
   	
	# getting raw data
    raw1 = light_sensor.getValue()			
    raw2 = light_sensor_l.getValue()		
    raw3 = light_sensor_r.getValue()		
    
    if raw1 > 0.58 or raw2 > 0.58 or raw3 > 0.58: #testing for red/green	
        led = True #Green	
    else:			
        led = False #Red			
    return led			
					
def getSensorValues():			
    #functions for getting lookup tables for reference nested in as args			
    #us_lookup table can probably be removed, it's a linear relationship between distance and			
    #time for signal to bounce back

	#getting raw data
    ir_raw = ir.getValue()			
    us_r_raw = us_right.getValue()			
    us_l_raw = us_left.getValue()  			
    distances = [] 			
    ir_lookup = ir.getLookupTable()			
    			
    distances.append(us_r_raw/5700) #raw value of ultrasonics is in microseconds, divide by 5700 to get dist. in m			
    distances.append(us_l_raw/5700)			
    			
    if ir_raw < 0.45 and ir_raw >= 0.42:			
        distances.append(1.5)			 			
    if ir_raw < 0.42:			
        distances.append(1.5)						
        			
    #Return distance, given raw voltage output from IR sensor			
    for i in range (1,int(len(ir_lookup)/3)):			
        #V decreases going down, D increases going down			
        v_high = ir_lookup[3*(i-1)+1]			
        v_low = ir_lookup[3*i+1] 			
        d_low = ir_lookup[3*(i-1)]			
        d_high = ir_lookup[3*i] 					
        if ir_raw >= v_low:			
            ir_distance = d_low + (d_high - d_low)*(v_high-ir_raw)/(v_high-v_low)			
            distances.append(ir_distance)			
            break			
        else:			
            i+=1						
    distances.append(getBearingInDegrees())			
    return distances	
    		
def getBearingInDegrees(): # uses the compass value to give the robots bearing in degrees			
    north = compass.getValues()	#getting compass vector								
    rad = math.atan2(north[2],north[0])	#calculating bearing from trigonometry		
    bearing = 90 - rad/math.pi*180.0 			
    if bearing < 0:			
        bearing += 360			
    return bearing	

#=================================ROTATION FUNCTIONS=============================    		
def rotateTheta(theta):	#robot will rotate theta degrees clockwise		
    angle_rotated = 0			
    initial_bearing = getBearingInDegrees()			
    rotate_CW() # starts rotating clockwise			
    while robot.step(TIME_STEP) != -1:			
        bearing = getBearingInDegrees()  			
        #Get bearing of block from where I am 			
        if (bearing - initial_bearing) >= -0.1:    #If i'm not pointing at block, angle to rotated is different			
            angle_rotated = bearing - initial_bearing			
        else: 			
            angle_rotated = bearing - initial_bearing + 360			
        if angle_rotated > theta:   # once the robot has rotated theta the rotation stops                                         			
            motor_left.setVelocity(0)			
            motor_right.setVelocity(0)			
            break	#  exit while loop		
    			
def rotateUntilBearing(target_bearing, initial_bearing):  # rotates until a specific bearing is reached	
    angle_rotated = 0	
    motor_left.setPosition(float('inf'))	
    motor_right.setPosition(float('inf'))
    if target_bearing == 0:
        rotate_CW()
        previousbearing = getBearingInDegrees()		
        while robot.step(TIME_STEP) != -1:     		
            bearing = getBearingInDegrees()	
            if bearing<previousbearing - 0.1:		
                motor_left.setVelocity(0)		
                motor_right.setVelocity(0)		
                break	#  exit while loop
            previousbearing = bearing
    if target_bearing > initial_bearing and target_bearing-initial_bearing <= 180:	# clocksize is quickest
        rotate_CW()	
        while robot.step(TIME_STEP) != -1:     	
            bearing = getBearingInDegrees() # constantly returns bearing	
            if bearing >= target_bearing - 0.1: # stops rotation once the current bearing equals the target bearing	
                motor_left.setVelocity(0)	
                motor_right.setVelocity(0)	
                break	#  exit while loop
    if target_bearing > initial_bearing and target_bearing-initial_bearing > 180: #anticlockwise is quickest
        rotate_ACW()
        while robot.step(TIME_STEP) != -1:     	
            bearing = getBearingInDegrees() # constantly returns the robots bearing
		#calculated angle rotated
            if bearing-initial_bearing > -0.1:
                angle_rotated = initial_bearing + 360 - bearing
            if bearing-initial_bearing <= 0.1:
                angle_rotated = initial_bearing - bearing	
            if angle_rotated >= 360 - target_bearing + initial_bearing:	# stops rotation once target bearing is reached
                motor_left.setVelocity(0)	
                motor_right.setVelocity(0)	
                break #  exit while loop
    if target_bearing < initial_bearing and initial_bearing-target_bearing <= 180: #anticlockwise is quickest	
        rotate_ACW()	
        while robot.step(TIME_STEP) != -1:	
            bearing = getBearingInDegrees()	# constantly returns the robots bearing
            if bearing <= target_bearing + 0.1:		# stops rotation once target bearing is reached
                motor_left.setVelocity(0)	
                motor_right.setVelocity(0) 	
                break   #  exit while loop
    if target_bearing < initial_bearing and initial_bearing-target_bearing > 180: #clockwise is quickest	
        rotate_CW()    	
        while robot.step(TIME_STEP) != -1:			
            bearing = getBearingInDegrees()  # constantly returns the robots bearing					
            if (bearing - initial_bearing) >= -0.1:    #If i'm not pointing at block, angle to rotated is different			
                angle_rotated = bearing - initial_bearing			
            else: 			
                angle_rotated = bearing - initial_bearing + 360			
            if angle_rotated >= 360-initial_bearing+target_bearing:                                            			
                motor_left.setVelocity(0)			
                motor_right.setVelocity(0)			
                break  #  exit while loop
                        
#INITIAL SCANNING FUNCTION               			
def doScan(theta, initial_bearing):
    close_arms() # arms must be closed so sensors work correctly			
    sensorValueScan = [] #currently looks like a 1D list, but will have lists appended to it to make it 2D			
    angle_rotated = 0			
    # set the target position, velocity of the motors			
    rotate_CW() # robot rotates while it scans	
    i = 0			
    			
    while robot.step(TIME_STEP) != -1:			
        bearing = getBearingInDegrees()	# constantly returns robots bearing		
        values = getSensorValues()	# gets sensor values		
        sensorValueScan.append(values)	# add the sensor values to the list
        			         			
        i += 1			
        	# returns angle rotated		
        if (bearing - initial_bearing) >= -0.1:			
            angle_rotated = bearing - initial_bearing			
        if bearing - initial_bearing < -0.1:			
            angle_rotated = bearing + (360 - initial_bearing)			
        if angle_rotated > theta:	# stops scan after the robot has rotated theta		
            motor_left.setVelocity(0)			
            motor_right.setVelocity(0)			
            break	# exit while loop - stops the scanning		
     			
    return sensorValueScan
    			
#CLEANING BLOCK DATA			
#Function to get block GPS coordinates, also bearings and distances			
def getBlockData(): 			
    blockBearings = [] #Will be 1D list			
    blockDistances = [] #Will be 1D list			
    blockGPS = [] #Will be 2D list, N*2, where ideally, N = 8. Expect errors to creep in at first.			
    ir_lookup = ir.getLookupTable() # infared sensor look up table			
    numCounter = 0			
    sumDistance = 0			
    for i in range(len(sensorValueScan)): #number of rows in sensorValueScan			
        sumDistance += sensorValueScan[i][2]			
        if sensorValueScan[i][2] != 0:			
            numCounter += 1			
    avgDistance = sumDistance/numCounter			
    for i in range(1,len(sensorValueScan)) :			
        alpha = sensorValueScan[i][2];			
    #Conditions for blocks to be picked out: large jump from previous value		
        if (sensorValueScan[i - 1][2] - alpha) > 0.12:			
            blockBearings.append(sensorValueScan[i][3]) # appends the blocks bearing			
            blockDistances.append(alpha)	# appends the blocks distance
		#finds the blocks bearing
    for i in range(len(blockBearings)):			
        xcoord = gps.getValues()[0] + (blockDistances[i] + 0.12) * math.cos(blockBearings[i] * math.pi / 180);			
        zcoord = gps.getValues()[2] + (blockDistances[i] + 0.12) * math.sin(blockBearings[i] * math.pi / 180);			
        blockGPS.append([xcoord,zcoord]) # appends the list with the blocks coords						
    return blockGPS, blockBearings, blockDistances
    		
#function to check if the robot's path to the block it's moving towards 	
#passes through a starting square 	
#returnTrip is a Boolean to check if the robot is on its way out or its way back  			
def checkStartCross(targetxpos, targetzpos, returnTrip = False): 			
    			
    nsamples = 20	
    reroute = False
    startval = 1			
    			 			
    current_position = gps.getValues()	
					
    if abs(current_position[0]) < 0.2 and 0.2 < abs(current_position[2]) < 0.6:
        startval = 10	
		
    for j in range(startval, nsamples): #starts at j=startval so a false positive isn't raised at the start			
        xsampledpos = (current_position[0] + ((j/nsamples)*(targetxpos - current_position[0])))			
        zsampledpos = (current_position[2] + ((j/nsamples)*(targetzpos - current_position[2])))	
        #print(xsampledpos, zsampledpos)					
        if abs(xsampledpos) < 0.2 and 0.2 < abs(zsampledpos) < 0.6 and returnTrip == False:			
            #print ("Line passes through either red or green starting square")	
            reroute = True	
        if abs(xsampledpos) < 0.2 and 0.2 < zsampledpos < 0.6 and returnTrip == True:	
            #print ("Line passes through red starting square")	
            reroute = True			
    			
    return reroute 	
    	
#======================= Navigation function for going around starting squares =====================	
def alternateRoute(desiredxpos, desiredzpos, switchingsides = False):
    motor_left.setVelocity(0.0)		
    motor_right.setVelocity(0.0)
    xdiff = 1
    zdiff = 1
    distance = 1
    zfirst = True
    twopointturn = False
    
    if abs(gps.getValues()[0]) < 0.2 and abs(desiredxpos) < 0.2:
        #print("2 turns needed to navigate around squares along z-line")
        twopointturn = True
    #elif 0.2 < abs(gps.getValues()[2]) < 0.6 and 0.2 < abs(desiredzpos) < 0.6:
        #print("This shouldn't happen in two halves! What have you done?")
    elif abs(gps.getValues()[0]) < 0.2 and abs(desiredxpos) > 0.2:
        #print("x needs to be done first")
        zfirst = False
    elif abs(gps.getValues()[0]) > 0.2 and abs(desiredxpos) < 0.2:
        #print("z needs to be done first")
        zfirst = True
    
    if getBearingToPoint(desiredxpos, 0, desiredzpos) < 90:
        xbearing = 0
        zbearing = 90
    elif 90 < getBearingToPoint(desiredxpos, 0, desiredzpos) < 180:
        xbearing = 180
        zbearing = 90
    elif 180 < getBearingToPoint(desiredxpos, 0, desiredzpos) < 270:
        xbearing = 180
        zbearing = 270
    else:
        xbearing = 0
        zbearing = 270
    if twopointturn == False:
        if zfirst == True:
            rotateUntilBearing(zbearing, getBearingInDegrees())
            move_forwards()  
            close_arms()	
            	
            while robot.step(TIME_STEP) != -1 and abs(zdiff) > 0.2:	       		
                zdiff = desiredzpos - gps.getValues()[2] - 0.02
                #print("zdiff", zdiff)
            
            bearingtopoint = getBearingToPoint(desiredxpos, 0, desiredzpos)  
            rotateUntilBearing(bearingtopoint, getBearingInDegrees())
            move_forwards()
                
            while robot.step(TIME_STEP) != -1 and distance > 0.1:	       		
                xdiff = desiredxpos - gps.getValues()[0]		
                zdiff = desiredzpos - gps.getValues()[2]		
                distance = math.sqrt(xdiff**2 + zdiff**2)
                #print("dist", distance)
                #print(gps.getValues()[0], gps.getValues()[2])
                if distance < 0.35 and switchingsides == False:
                    open_arms()
        
        else:
            rotateUntilBearing(xbearing, getBearingInDegrees())
            move_forwards()  	
            close_arms()
            	
            while robot.step(TIME_STEP) != -1 and abs(xdiff) > 0.2:	       		
                xdiff = desiredxpos - gps.getValues()[0] - 0.02
              
            bearingtopoint = getBearingToPoint(desiredxpos, 0, desiredzpos)  
            rotateUntilBearing(bearingtopoint, getBearingInDegrees())
            move_forwards()
    
            while robot.step(TIME_STEP) != -1 and distance > 0.1:	       		
                xdiff = desiredxpos - gps.getValues()[0]		
                zdiff = desiredzpos - gps.getValues()[2]		
                distance = math.sqrt(xdiff**2 + zdiff**2)
                if distance < 0.35:
                    open_arms()
            
    else:
        if firstHalf == True:
            rotateUntilBearing(180, getBearingInDegrees())
            move_forwards()
            close_arms()
            
            while robot.step(TIME_STEP) != -1 and abs(xdiff) > 0.15:	       		
                xdiff = -0.6 - gps.getValues()[0] - 0.02
                
            rotateUntilBearing(zbearing, getBearingInDegrees())
            move_forwards()
            
            while robot.step(TIME_STEP) != -1 and abs(zdiff) > 0.15:
                    zdiff = desiredzpos - gps.getValues()[2]
                    
            bearingtopoint = getBearingToPoint(desiredxpos, 0, desiredzpos)  
            rotateUntilBearing(bearingtopoint, getBearingInDegrees())
            move_forwards()
        
            while robot.step(TIME_STEP) != -1 and distance > 0.07:	       		
                xdiff = desiredxpos - gps.getValues()[0]		
                zdiff = desiredzpos - gps.getValues()[2]		
                distance = math.sqrt(xdiff**2 + zdiff**2)
                if distance < 0.35:
                    open_arms()            
        else:
            rotateUntilBearing(0, getBearingInDegrees())
            move_forwards()
            close_arms()
            
            while robot.step(TIME_STEP) != -1 and abs(xdiff) > 0.15:	       		
                xdiff = 0.6 - gps.getValues()[0] - 0.02
                
            rotateUntilBearing(zbearing, getBearingInDegrees())
            move_forwards()
            
            while robot.step(TIME_STEP) != -1 and abs(zdiff) > 0.15:
                    zdiff = desiredzpos - gps.getValues()[2]
                    
            bearingtopoint = getBearingToPoint(desiredxpos, 0, desiredzpos)  
            rotateUntilBearing(bearingtopoint, getBearingInDegrees())
            move_forwards()
        
            while robot.step(TIME_STEP) != -1 and distance > 0.07:	       		
                xdiff = desiredxpos - gps.getValues()[0]		
                zdiff = desiredzpos - gps.getValues()[2]		
                distance = math.sqrt(xdiff**2 + zdiff**2)
                if distance < 0.35:
                    open_arms()    
        
#Gets a bearing when given a position  
#DO NOT CHANGE THE FUNCTION BASIC ARGUMENTS, -0.4 IS VERY IMPORTANT          
def getBearingToPoint(x = 0, y = 0, z = -0.4):	
    initial_position = [x, y, z]	# initial position refers to the start position of the robot on the square but this function can be used for a general position		
    current_position = gps.getValues()	# get the robots current position		
    target_bearing = 0.0 # initialise target bearing - may not be needed now?	
	# logic to give the bearing to a point based on which quadrant the robot is in
    if current_position[2] < initial_position[2]:			
        target_bearing = 90.0 - (math.atan((current_position[0] - initial_position[0]) / (current_position[2] - initial_position[2])) * 180.0 / math.pi)								
    if current_position[2] > initial_position[2]:			
        target_bearing = 270.0 - (math.atan((current_position[0] - initial_position[0]) / (current_position[2] - initial_position[2])) * 180.0 / math.pi)						
    if current_position[2] == initial_position[2] and current_position[0] > initial_position[0]:			
        target_bearing = 180.0					
    if current_position[2] == initial_position[2] and current_position[0] < initial_position[0]:			
        target_bearing = 0.0							 	
    return target_bearing  

#======================= Return to initial position =====================			
def returnToStart(): # robot returns to its start position on the square					
    target_bearing = getBearingToPoint() # find bearing to start position - no arguments needed as getBearingToPoint takes the start position as defult					
    initial_bearing = getBearingInDegrees()			
    rotateUntilBearing(target_bearing, initial_bearing)	# robot points at start position		
    move_forwards()	# moves towards start position		
    while robot.step(TIME_STEP) != -1:			
          distance = math.sqrt((gps.getValues()[0])**2 + (-0.4 - gps.getValues()[2])**2); # constantly calculated the distamce to the square		
          if distance <= 0.2:	# stops once the robot reaches the square	
              motor_left.setVelocity(0)			
              motor_right.setVelocity(0)			
              break					
          if robot.step(TIME_STEP) == 1:			
              break	
              
#=================================MAIN CODE=====================================================			
#robot instance already created and devices enabled with timestep			
#initialize indexing and booleans to track robot process			
i=0			
scanblocks = False			
gotblock = False			
moveblock = False			
blockgreen = False 			
wrongBlocks = []
rightBlocks = []
firstHalf = True	
otherRobotFinished = False
gotallblock = False
cross = 0		
	
while robot.step(TIME_STEP) != -1:			

#=========================FIRST HALF============================================
    if firstHalf == True: # robot collects blocks in only one half
       
        #SCANNING FOR BLOCKS
        if scanblocks == False:			
            current_bearing = getBearingInDegrees()			
            sensorValueScan = doScan(355, current_bearing)	# scan for blocks			
            scanblocks = True	# scan completed, boolean changed so next section can happen	
    
        #GETTING BLOCK DATA		
        if scanblocks==True and gotblock == False:	

            GPSOfBlocks, bearings, distances = getBlockData()	#block data
            indicesToRemove = []	
            indicesToRemoveForWrongHalf = []	

#=====================CLEANING BLOCK DATA============================================
       	
            #REMOVING BLOCKS THAT ARE ALREADY IN THE RIGHT PLACE	
            for i in range(len(GPSOfBlocks)):	
                if abs(GPSOfBlocks[i][0]) < 0.2 and 0.2 < abs(GPSOfBlocks[i][1]) < 0.6:		
                    indicesToRemove.append(i)	
            
            for i in range(len(GPSOfBlocks)):
                if abs(GPSOfBlocks[i][0]) > 1.1 or abs(GPSOfBlocks[i][1]) > 1.1:
                    indicesToRemove.append(i)
                        
            #It is very important that we delete the higher index first, so that 	
            #by deleting indices one by one, we are not affecting remaining deletions	
            #And you know that indicesToRemove has indices in ascending order	
            #So iterate through backwards	
            for index in sorted(indicesToRemove, reverse=True):		
                try:	  	
                    GPSOfBlocks.pop(index)	
                    bearings.pop(index)	
                    distances.pop(index)
                except IndexError:
                    pass		
                
            #REMOVING BLOCKS THAT HAVE ALREADY BEEN VISITED		
            if int(len(wrongBlocks)) > 0:	
                indicesToRemove = []		
                            
                for i in range(len(GPSOfBlocks)):			
                    for j in range(len(wrongBlocks)):				
                        #looking at the difference between GPS locations of wrong coloured blocks and blocks from scanning again			
                        xdelta = wrongBlocks[j][0]-GPSOfBlocks[i][0]			
                        zdelta = wrongBlocks[j][1]-GPSOfBlocks[i][1]				
                        distanceBetweenReadings = math.sqrt(xdelta**2 + zdelta**2)			
                                
                        if distanceBetweenReadings < 0.15:			
                            #This means the same block is being read again. Delete it from the front of the list			
                            indicesToRemove.append(i)	
                                
                #Same logic as above; we must iterate backwards         	                       		
                for index in sorted(indicesToRemove,reverse=True):	  	
                    try:	  	
                        GPSOfBlocks.pop(index)	
                        bearings.pop(index)	
                        distances.pop(index)
                    except IndexError:
                        pass
            
            #REMOVING BLOCKS WITH THE WRONG X COORDINATE ie on the other size of the board
            for i in range(len(GPSOfBlocks)):
                if GPSOfBlocks[i][0] >= 0:
                    indicesToRemoveForWrongHalf.append(i)
            
            for index in sorted(indicesToRemoveForWrongHalf, reverse=True):		
                try:	  	
                    GPSOfBlocks.pop(index)	
                    bearings.pop(index)	
                    distances.pop(index)
                except IndexError:
                    pass
                
#===========================NOW GOING TO ANY UNVISITED BLOCKS=============================

            #Check if you will need to go around. Try-except handles cases of empty GPS lists
            #i.e. finished	
            try:
                checkgoround = checkStartCross(GPSOfBlocks[0][0], GPSOfBlocks[0][1])
            except IndexError:
                sendFinished()
                firstHalf = False
            
            #If we don't need to reroute, run Cindy's orginal code as normal	
            if checkgoround == False and firstHalf == True:	
                rotateUntilBearing(bearings[0], getBearingInDegrees())	
                move_forwards()	
                close_arms()		  		
                n = 1
                		
                while robot.step(TIME_STEP) != -1:
                    
                    try:	       			
                        xdiff = GPSOfBlocks[0][0] - gps.getValues()[0]			
                        zdiff = GPSOfBlocks[0][1] - gps.getValues()[2]			
                        distance = math.sqrt(xdiff**2 + zdiff**2)		
                        
                        n+=1
                        
                        if distance < 0.4: # opens arms at the right time
                            open_arms()
                        		
                        if distance < 0.1:	# stops just in front of the block		
                            motor_left.setVelocity(0)			
                            motor_right.setVelocity(0)
                            close_arms() # grabs block
                            wait()			
                            colour = getColour(); # gets the colour of the block	
                            if colour == False:			
                                print("Green bot has located a red block")
                                open_arms() # releases block			
                                shuffle_back_short()			
                                scanblocks=False			
                                wrongBlocks.append(GPSOfBlocks[0])			
                                break					
                            elif colour == True:					
                                blockgreen=True			
                                print("Green bot has located a green block")		
                                moveblock = False			
                                gotblock = True			
                                break
                                      
                        if n == 600:
                            motor_left.setVelocity(0)			
                            motor_right.setVelocity(0)
                            close_arms()
                            wait()			
                            colour = getColour();	
                            if colour == False:			
                                print("Green bot has located a red block")
                                open_arms()			
                                shuffle_back_short()			
                                scanblocks=False			
                                wrongBlocks.append(GPSOfBlocks[0])			
                                break					
                            elif colour == True:					
                                blockgreen=True			
                                print("Green bot has located a green block")		
                                moveblock = False			
                                gotblock = True			
                                break
                    
                    #If the lists are empty, consider first half completed            	
                    except IndexError:
                        sendFinished()
                        firstHalf = False
                        break
                        
            #Rerouting code version to get to block        
            if checkgoround == True and firstHalf == True:       	
                try:
                    x,y = GPSOfBlocks[0][0], GPSOfBlocks[0][1]
                except IndexError:
                    firstHalf = False
                    sendFinished()
                    
                alternateRoute(x, y)	
                motor_left.setVelocity(0)			
                motor_right.setVelocity(0)	
                close_arms()
                wait()		
                colour = getColour();		
                if colour == False:			
                    print("Green bot has located a red block")	
                    open_arms()		
                    shuffle_back_short()			
                    scanblocks=False			
                    wrongBlocks.append(GPSOfBlocks[0])			
                elif colour == True:					
                    blockgreen=True			
                    print("Green bot has located a green block")			
                    moveblock = False			
                    gotblock = True
                    		
#=======================TAKING BLOCK BACK TO START=============================           
                	        	
        #TAKING BLOCK TO START POINT     			
        if moveblock == False and blockgreen==True:	
            altRoute = checkStartCross(0, -0.4, True)				
            if altRoute == False:	
                returnToStart()	# go straight to square
            else:	
                bearings[0] = getBearingToPoint()	
                alternateRoute(0, -0.4)			
            open_arms()
            if 265 < getBearingInDegrees() < 275:
                shuffle_back_shortest()
            else:			
                shuffle_back()			
            moveblock = True			
            gotblock = False			
            scanblocks = False	
    
#=============SWITCH OVER AND START SECOND HALF=======================================
    #If a robot is finished and has not yet got data from the robot, it will sit and 
    #attempt to receive data. This loop ends once all data is passed on.#
    j = 0
    while firstHalf == False and otherRobotFinished == False:
        if receiver.getQueueLength() != 0:
            otherRobotFinished = True # green knows other robot has finished
        else:
            j += 1
            if j == 100:
                break
    #Now going to collect and bring back all blocks in turn
    if firstHalf == False and otherRobotFinished == True:
        if cross == 0:
            #print("green heading across")
            scanblocks = False
            gotblock = False
            #print("first half not done")
            alternateRoute(0.8, -0.8, True)
            #print("first half done")
            alternateRoute(0.8, 0, True)
            motor_left.setVelocity(0)			
            motor_right.setVelocity(0)
            cross = 1
        
        if scanblocks == False:			
            current_bearing = getBearingInDegrees()			
            sensorValueScan = doScan(355, current_bearing)				
            scanblocks = True
        
        #GETTING BLOCK DATA		
        if scanblocks==True and gotblock == False:	

            GPSOfBlocks, bearings, distances = getBlockData()	
            indicesToRemove = []	
            indicesToRemoveForWrongHalf = []	

#=====================CLEANING BLOCK DATA============================================
       	
            #REMOVING BLOCKS THAT ARE ALREADY IN THE RIGHT PLACE	
            for i in range(len(GPSOfBlocks)):	
                if abs(GPSOfBlocks[i][0]) < 0.2 and 0.2 < abs(GPSOfBlocks[i][1]) < 0.6:		
                    indicesToRemove.append(i)	
            
            for i in range(len(GPSOfBlocks)):
                if abs(GPSOfBlocks[i][0]) > 1.15 or abs(GPSOfBlocks[i][1]) > 1.15:
                    indicesToRemove.append(i)
                     
            #It is very important that we delete the higher index first, so that 	
            #by deleting indices one by one, we are not affecting remaining deletions	
            #And you know that indicesToRemove has indices in ascending order	
            #So iterate through backwards	
            for index in sorted(indicesToRemove, reverse=True):		
                try:	  	
                    GPSOfBlocks.pop(index)	
                    bearings.pop(index)	
                    distances.pop(index)
                except IndexError:
                    pass		
                
            #REMOVING BLOCKS THAT HAVE ALREADY BEEN VISITED		
            if int(len(wrongBlocks)) > 0:	
                indicesToRemove = []		
                            
                for i in range(len(GPSOfBlocks)):			
                    for j in range(len(wrongBlocks)):				
                        #looking at the difference between GPS locations of wrong coloured blocks and blocks from scanning again			
                        xdelta = wrongBlocks[j][0]-GPSOfBlocks[i][0]			
                        zdelta = wrongBlocks[j][1]-GPSOfBlocks[i][1]				
                        distanceBetweenReadings = math.sqrt(xdelta**2 + zdelta**2)			
                                
                        if distanceBetweenReadings < 0.15:			
                            #This means the same block is being read again. Delete it from the front of the list			
                            indicesToRemove.append(i)	
                                
                #Same logic as above; we must iterate backwards         	                       		
                for index in sorted(indicesToRemove,reverse=True):	  	
                    try:	  	
                        GPSOfBlocks.pop(index)	
                        bearings.pop(index)	
                        distances.pop(index)
                    except IndexError:
                        pass
            
            #REMOVING BLOCKS WITH THE WRONG X COORDINATE 
            for i in range(len(GPSOfBlocks)):
                if GPSOfBlocks[i][0] < 0:
                    indicesToRemoveForWrongHalf.append(i)
            
            for index in sorted(indicesToRemoveForWrongHalf, reverse=True):		
                try:	  	
                    GPSOfBlocks.pop(index)	
                    bearings.pop(index)	
                    distances.pop(index)
                except IndexError:
                    pass
                
#===========================NOW GOING TO ANY UNVISITED BLOCKS=============================
            for j in range(len(GPSOfBlocks)):
                #Check if you will need to go around. Try-except handles cases of empty GPS lists
                #i.e. finished	
                checkgoround = checkStartCross(GPSOfBlocks[j][0], GPSOfBlocks[j][1])
                
                #If we don't need to reroute, run Cindy's orginal code as normal	
                if checkgoround == False and firstHalf == False:
                    #print("normal route")	
                    rotateUntilBearing(getBearingToPoint(GPSOfBlocks[j][0], 0, GPSOfBlocks[j][1]), getBearingInDegrees())		
                    move_forwards()			
                    close_arms()
                    n = 1   		
                    		
                    while robot.step(TIME_STEP) != -1:	       			
                        xdiff = GPSOfBlocks[j][0] - gps.getValues()[0]			
                        zdiff = GPSOfBlocks[j][1] - gps.getValues()[2]			
                        distance = math.sqrt(xdiff**2 + zdiff**2)	
                        
                        n += 1
                        
                        if distance < 0.35:
                            open_arms_wide()	
	
                        if distance < 0.1:			
                            motor_left.setVelocity(0)			
                            motor_right.setVelocity(0)	
                            close_arms()				
                            blockgreen=True			
                            moveblock = False				
                            break
                            
                        if n == 600:
                            motor_left.setVelocity(0)			
                            motor_right.setVelocity(0)
                            close_arms()
                            wait()			
                            colour = getColour();	
                            if colour == False:			
                                #print("Green bot has located a red block")
                                open_arms()			
                                shuffle_back_short()			
                                scanblocks=False			
                                wrongBlocks.append(GPSOfBlocks[0])			
                                break					
                            elif colour == True:					
                                blockgreen=True			
                                #print("Green bot has located a green block")		
                                moveblock = False			
                                gotblock = True			
                                break
                            
                #Rerouting code version to get to block        
                if checkgoround == True and firstHalf == False:
                    #print("altroute")       	
                    x,y = GPSOfBlocks[j][0], GPSOfBlocks[j][1]	
                        
                    alternateRoute(x, y)	
                    motor_left.setVelocity(0)			
                    motor_right.setVelocity(0)
                    close_arms()					
                    blockgreen=True
                    moveblock = False						
                        		
    #=======================TAKING BLOCK BACK TO START=============================           
                    	        	
                #TAKING BLOCK TO START POINT     			
                if moveblock == False and blockgreen==True:	
                    altRoute = checkStartCross(0, -0.4, True)				
                    if altRoute == False:	
                        returnToStart()	
                    else:	
                        bearings[0] = getBearingToPoint()	
                        alternateRoute(0, -0.4)
                    motor_left.setVelocity(0)			
                    motor_right.setVelocity(0)			
                    open_arms()			
                    shuffle_back()			
                    moveblock = True
                    gotblock = False			
                    scanblocks = False
                    			
        gotallblock = True
        
    if gotallblock ==True:
        if firstHalf == False and otherRobotFinished == True:
            scanblocks = False
            gotblock = False
            motor_left.setVelocity(0)			
            motor_right.setVelocity(0)
            
            if scanblocks == False:			
                current_bearing = getBearingInDegrees()			
                sensorValueScan = doScan(355, current_bearing)				
                scanblocks = True
            
            #GETTING BLOCK DATA		
            if scanblocks==True and gotblock == False:	
        
                    
                #if nextTargetIdentified == False:	
                GPSOfBlocks, bearings, distances = getBlockData()	
                indicesToRemove = []	
                indicesToRemoveForWrongHalf = []	
    
    #=====================CLEANING BLOCK DATA============================================
           	
                #REMOVING BLOCKS THAT ARE ALREADY IN THE RIGHT PLACE	
                for i in range(len(GPSOfBlocks)):	
                    if abs(GPSOfBlocks[i][0]) < 0.2 and 0.2 < abs(GPSOfBlocks[i][1]) < 0.6:		
                        indicesToRemove.append(i)	
                
                for i in range(len(GPSOfBlocks)):
                    if abs(GPSOfBlocks[i][0]) > 1.12 or abs(GPSOfBlocks[i][1]) > 1.12:
                        indicesToRemove.append(i)
                         
                #It is very important that we delete the higher index first, so that 	
                #by deleting indices one by one, we are not affecting remaining deletions	
                #And you know that indicesToRemove has indices in ascending order	
                #So iterate through backwards	
                for index in sorted(indicesToRemove, reverse=True):		
                    try:	  	
                        GPSOfBlocks.pop(index)	
                        bearings.pop(index)	
                        distances.pop(index)
                    except IndexError:
                        pass	
                    
                #REMOVING BLOCKS THAT HAVE ALREADY BEEN VISITED		
                if int(len(wrongBlocks)) > 0:	
                    indicesToRemove = []		
                                
                    for i in range(len(GPSOfBlocks)):			
                        for j in range(len(wrongBlocks)):				
                            #looking at the difference between GPS locations of wrong coloured blocks and blocks from scanning again			
                            xdelta = wrongBlocks[j][0]-GPSOfBlocks[i][0]			
                            zdelta = wrongBlocks[j][1]-GPSOfBlocks[i][1]				
                            distanceBetweenReadings = math.sqrt(xdelta**2 + zdelta**2)			
                                    
                            if distanceBetweenReadings < 0.15:			
                                #This means the same block is being read again. Delete it from the front of the list			
                                indicesToRemove.append(i)	
                                    
                    #Same logic as above; we must iterate backwards         	                       		
                    for index in sorted(indicesToRemove,reverse=True):	  	
                        try:	  	
                            GPSOfBlocks.pop(index)	
                            bearings.pop(index)	
                            distances.pop(index)
                        except IndexError:
                            pass
                
                #REMOVING BLOCKS WITH THE WRONG X COORDINATE 
                for i in range(len(GPSOfBlocks)):
                    if GPSOfBlocks[i][0] < 0:
                        indicesToRemoveForWrongHalf.append(i)
                
                for index in sorted(indicesToRemoveForWrongHalf, reverse=True):		
                    try:	  	
                        GPSOfBlocks.pop(index)	
                        bearings.pop(index)	
                        distances.pop(index)
                    except IndexError:
                        pass
                    
    #===========================NOW GOING TO ANY UNVISITED BLOCKS=============================
                for j in range(len(GPSOfBlocks)):
                    #Check if you will need to go around. Try-except handles cases of empty GPS lists
                    #i.e. finished	
                    checkgoround = checkStartCross(GPSOfBlocks[j][0], GPSOfBlocks[j][1])
                    
                    #If we don't need to reroute, run Cindy's orginal code as normal	
                    if checkgoround == False and firstHalf == False:
                        #print("normal route")	
                        rotateUntilBearing(getBearingToPoint(GPSOfBlocks[j][0], 0, GPSOfBlocks[j][1]), getBearingInDegrees())		
                        move_forwards()			
                        close_arms()
                        n = 1   		
                        		
                        while robot.step(TIME_STEP) != -1:	       			
                            xdiff = GPSOfBlocks[j][0] - gps.getValues()[0]			
                            zdiff = GPSOfBlocks[j][1] - gps.getValues()[2]			
                            distance = math.sqrt(xdiff**2 + zdiff**2)	
                            
                            n += 1
                            
                            if distance < 0.35:
                                open_arms_wide()	
    	
                            if distance < 0.1:			
                                motor_left.setVelocity(0)			
                                motor_right.setVelocity(0)	
                                close_arms()				
                                blockgreen=True			
                                moveblock = False					
                                break
                                
                            if n == 600:
                                motor_left.setVelocity(0)			
                                motor_right.setVelocity(0)
                                close_arms()
                                wait()			
                                colour = getColour();	
                                if colour == False:			
                                    #print("Green bot has located a red block")
                                    open_arms()			
                                    shuffle_back_short()			
                                    scanblocks=False			
                                    wrongBlocks.append(GPSOfBlocks[0])			
                                    break					
                                elif colour == True:					
                                    blockgreen=True			
                                    #print("Green bot has located a green block")		
                                    moveblock = False			
                                    gotblock = True			
                                    break
                                
                    #Rerouting code version to get to block        
                    if checkgoround == True and firstHalf == False:
                        #print("altroute")       	
                        x,y = GPSOfBlocks[j][0], GPSOfBlocks[j][1]	
                            
                        alternateRoute(x, y)	
                        motor_left.setVelocity(0)			
                        motor_right.setVelocity(0)
                        close_arms()					
                        blockgreen=True
                        moveblock = False						
                            		
        #=======================TAKING BLOCK BACK TO START=============================           
                        	        	
                    #TAKING BLOCK TO START POINT     			
                    if moveblock == False and blockgreen==True:	
                        altRoute = checkStartCross(0, -0.4, True)				
                        if altRoute == False:	
                            returnToStart()	
                        else:	
                            bearings[0] = getBearingToPoint()	
                            alternateRoute(0, -0.4)
                        motor_left.setVelocity(0)			
                        motor_right.setVelocity(0)			
                        open_arms()			
                        shuffle_back()			
                        moveblock = True
                        gotblock = False			
                        scanblocks = False
        returnToStart()
        print("Green finished")
        break

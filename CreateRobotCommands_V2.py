def CreateRobotCommands(CurrentPos, CurrentDir, TargetPos):
    
    import math

    # Constants
    MOVE_FORWARD = [1, 2]
    MOVE_BACKWARD = [2, 1]
    TURN_CCW = [1, 1]
    TURN_CW = [2, 2]
    RPM = 40 # default for both straight and turn moves
    #GEAR_RATIO = 1 Because it's 1:1 it's not relevant
    WHEEL_RADIUS = 45 # in mm (outside)
    TIME_CCW = 5.65 # in seconds, default for CCW turns
    TIME_CW = 5.55 # in seconds, default for CW turns
    SQUARE_SIZE = 50 # in mm, for grid


    # Determine TargetDir and Distance
    Ydist = TargetPos[0] - CurrentPos[0]
    Xdist = TargetPos[1] - CurrentPos[1]
    if Ydist == 0:
        CalcDistance = abs(Xdist)*SQUARE_SIZE #in mm
        print(CalcDistance)
        Distance = (CalcDistance+0.363)/1.372 # after fudging
        if Xdist > 0:
            TargetDir = 0
        else:
            TargetDir = 180
    else:
        CalcDistance = abs(Ydist)*SQUARE_SIZE #in mm
        print(CalcDistance)
        Distance = (CalcDistance+0.363)/1.372 # after fudging
        if Ydist > 0:
            TargetDir = 90
        else:
            TargetDir = 270
    
    print(TargetDir)

    # Determine the type of move required and return the commands
    if CurrentDir == TargetDir:
        if CurrentPos == TargetPos:
            return []
        else:
            TIME = (Distance / (2 * math.pi * WHEEL_RADIUS) ) / (RPM / 60)
            return MOVE_FORWARD, RPM, TIME
    else:
        TurnAngle = TargetDir - CurrentDir
        if   TurnAngle == 90 or TurnAngle == -270:
            return TURN_CCW, RPM, TIME_CCW
        elif TurnAngle == -90 or TurnAngle == 270:
            return TURN_CW, RPM, TIME_CW
        else:
            TIME = (Distance / (2 * math.pi * WHEEL_RADIUS) ) / (RPM / 60)
            return MOVE_BACKWARD, RPM, TIME


# Test

'''

MOTOR_DIRECTIONS, RPM, TIME = CreateRobotCommands([0, 0], 0, [0, 3])

print(TIME)

Time_Units = int(TIME)
Time_Decimals = int(round((TIME - Time_Units) * 100))


from MQTTwrite import MQTTwrite

MQTTwrite("M1_Dir", MOTOR_DIRECTIONS[0])
MQTTwrite("M2_Dir", MOTOR_DIRECTIONS[1])
MQTTwrite("M1_RPM", RPM)
MQTTwrite("M2_RPM", RPM)
MQTTwrite("Time_Units", Time_Units)
MQTTwrite("Time_Decimals", Time_Decimals)

'''
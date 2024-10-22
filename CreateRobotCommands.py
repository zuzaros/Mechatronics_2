def CreateRobotCommands(CurrentPos, CurrentDir, TargetPos):
    
    import math

    # Constants
    MOVE_FORWARD = [1, 1]
    MOVE_BACKWARD = [2, -1]
    TURN_CCW = [2, 1]
    TURN_CW = [1, 2]
    RPM = 30 # default for straight move
    WHEEL_RADIUS = 5 # in mm
    TIME = 5 # in seconds, default for turns
    SQUARE_SIZE = 50 # in mm

    # Determine TargetDir and Distance
    Ydist = TargetPos[0] - CurrentPos[0]
    Xdist = TargetPos[1] - CurrentPos[1]
    if Ydist == 0:
        Distance = abs(Xdist)*SQUARE_SIZE
        if Xdist > 0:
            TargetDir = 0
        else:
            TargetDir = 180
    else:
        Distance = abs(Ydist)*SQUARE_SIZE
        if Ydist > 0:
            TargetDir = 90
        else:
            TargetDir = 270


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
            return TURN_CCW, RPM, TIME
        elif TurnAngle == -90 or TurnAngle == 270:
            return TURN_CW, RPM, TIME
        else:
            TIME = (Distance / (2 * math.pi * WHEEL_RADIUS) ) / (RPM / 60)
            return MOVE_BACKWARD, RPM, TIME


# Test
#print(CreateRobotCommands([0, 20], 0, [0, 0]))


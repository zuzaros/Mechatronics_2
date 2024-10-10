# import the necessary libraries
from manualMissionControl import manualMissionControl
from automaticMissionControl import automaticMissionControl

# ask the user if they want to run the mission manually or automatically
print("Welcome to the Mission Control Center!")
print("Would you like to run the mission manually or automatically?")
print("Please type 'm' or 'a' to choose.")
missionType = input()

# run correct mission based on user input
# if they choose manual, run the manual mission
if missionType == 'm':
    manualMissionControl()
# if they choose automatic, run the automatic mission
elif missionType == 'a':
    automaticMissionControl()
# if they choose neither, print an error message
else:
    print("Invalid input. Please type 'm' or 'a' to choose.")

# end of missionControl.py

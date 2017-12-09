import time

def actualcurrentposition(curpos):
    if (curpos +- somenum) == ATTENTION:
        return "attention"
    elif (curpos +- somenum) == HORNSUP:
        return "hornsup"
    elif (curpos +- somenum) == TRAILARMS:
        return "trailarms"
    else:
        return "none"

def expectedposition(curtime):
    timediff = curtime - STARTTIME
    if timediff < MOVETOHORNSUP:
        return "attention"
    elif timediff < movetoattention:
        return "hornsup"
    elif timediff < MOVETOTRAILARMS:
        return "attention"
    elif timediff < MOVETOATTENTION:
        return "trailarms"
    else:
        return "none"

def getposition():
    # this method get the position of the watch



# these are the expected raw data positions, learned from previosly collected data, average of runs has been taken and a buffer is given to decide if actually in that position
ATTENTION = 
HORNSUP = 
TRAILARMS = 


# set up run, 5 clicks to stay at attention

# make 4 clicks


#start tracking motions
STARTTIME = time.time()
# starts in attention position for 5 seconds, keep clicks going
MOVETOHORNSUP = STARTTIME + 5
# from horns up position move back to attention for 5 seconds, keep clicks going
MOVETOATTENTION = MOVETOHORNSUP + 5
# from attention position move to trail arms for 5 seconds, keep clicks going
MOVETOTRAILARMS = MOVETOATTENTION + 5
# end the exercise
ENDTIME = MOVETOTRAILARMS + 5

runreview = []

while (time.time() < ENDTIME):
    curtime = time.time()
    curpos = getposition()
    # if actualcurrentposition(curpos) != expectedposition(curtime):
    #     # the person is not in the correct position, mark this as incorrect
    runreview.append({"time": curtime, "curposition": actualcurrentposition(curpos), "expposition": expectedposition(curtime)})

# send back plot to phone for review of that run, actual position and expected position vs time
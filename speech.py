## Speech bits taken out of main.py

import subprocess
process1 = subprocess.Popen(["echo", message], stdout=subprocess.PIPE)
process2 = subprocess.Popen(
    ["text2wave"], stdin=process1.stdout, stdout=subprocess.PIPE)
subprocess.Popen(["play", "-t", "wav", "-", "tempo",
                  str(0.8), "pitch", str(-100)], stdin=process2.stdout)




# Greeting message code

presetMessages = [
    "Nice weather today isn't it,",
    "Nice shirt,",
    "Have a wonderful day,",
    "Nice to see you here,",
    "I'm running out of greetings again",
    "I'm not being paid enough for this",
    "Good morning. No.   Wait. Good afternoon. No.   \
Wait. Good morning. No. Wait. Nevermind",
    "I think I've saw you before"
]

def getGreetingMessage(callingName):

    message = ''

    rand = int(random.random() * 2)

    if rand == 0:  # time based greeting
        currentHour = datetime.now().hour
        if currentHour >= 5 and currentHour <= 11:
            message += "Good morning,"
        elif currentHour >= 12 and currentHour <= 5:
            message += "Good afternoon,"
        elif currentHour >= 6 and currentHour <= 9:
            message += "Good evening,"
        else:
            message += "Good night,"
    else:  # vague greeting
        message += presetMessages[(int)(random.random() * len(presetMessages))]

    if callingName is not None:
        message += " " + callingName

    return message

###
greeted = False
        message = ''

        if not greeted:
            message = getGreetingMessage(None)
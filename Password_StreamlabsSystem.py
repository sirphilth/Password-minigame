#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Redeem script to redeem rewards for a cost for users"""
#---------------------------------------
# Libraries and references
#---------------------------------------
import codecs
import collections
import json
import os
import re
import sys
import time

import random
random = random.WichmannHill()
#---------------------------------------
# [Required] Script information
#---------------------------------------
ScriptName = "Password minigame"
Website = "https://www.twitch.tv/SirPhilthyOwl"
Creator = "SirPhilthyOwl"
Version = "1.0.0"
Description = "Password minigame for viewers"
#---------------------------------------
# Versions
#---------------------------------------
"""
1.0.0 Script made.
"""
#---------------------------------------
# Variables
#---------------------------------------
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
ReadMe = os.path.join(os.path.dirname(__file__), "README.txt")
FourLetterWords = os.path.join(os.path.dirname(__file__), "Words.txt")
Userfile = os.path.join(os.path.dirname(__file__), "Users.json")

#---------------------------------------
# Websocket
#---------------------------------------


def SendWebsocket(mode, string, guessList):
    if guessList == False:
        guessList = ["","","","",""]
    Parent.Log(ScriptName, "Sending: {}".format(str(Password.Guesses)))
    # Broadcast WebSocket Event
    payload = {
        "mode": mode,
        "Encrypt": string,
        "Guess1": guessList[0],
        "Guess2": guessList[1],
        "Guess3": guessList[2],
        "Guess4": guessList[3],
        "Guess5": guessList[4]
    }
    Parent.BroadcastWsEvent("EVENT_USERNAME", json.dumps(payload))
    return




#---------------------------------------
# Classes
#---------------------------------------

class Settings:
    """" Loads settings from file if file is found if not uses default values"""

    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsFile=None):
        if settingsFile and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')
        else: #set variables if no custom settings file is found
            self.PrefixCommand = "!password"
            self.QueueTime = 60
            self.GameTime = 60
            self.WinPoints = 1000
            self.PositionalColor = "rgba(255,0,0,255)"
            self.TextColor = "rgba(255,0,0,255)"
            self.GuessColor = "rgba(255,0,0,255)"



    # Reload settings on save through UI
    def ReloadSettings(self, data):
        """Reload settings on save through UI"""
        self.__dict__ = json.loads(data, encoding='utf-8-sig')
        return

    # Save settings to files (json and js)
    def SaveSettings(self, settingsFile):
        try:
            """Save settings to files (json and js)"""
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
                json.dump(self.__dict__, f, encoding='utf-8', ensure_ascii=False)
            with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8', ensure_ascii=False)))
        except ValueError:
            Parent.Log(ScriptName, "Failed to save settings to file.")
        return

class User:
    def __init__(self):
        self.PasswordDict = {}

    def Load(self):
        try:
            with codecs.open(Userfile, encoding='utf-8-sig', mode='r') as f:
                self.PasswordDict = json.load(f, encoding='utf-8-sig')
        except:
            Parent.Log(ScriptName, "Could not load json object.")

    def Save(self):
        with codecs.open(Userfile, encoding='utf-8-sig', mode='w+') as f:
            json.dump(self.PasswordDict, f, encoding='utf-8-sig')

    def Add(self, name):
        if not name in self.PasswordDict:
            self.PasswordDict[name] = {"Wins": 0, "Guesses": 0, "Time": 0}
        else:
            return

    def ChangeAttr(self, name, Attr, Number):
        if not Attr == "Time":
            self.PasswordDict[name][Attr] += Number
        else:
            self.PasswordDict[name][Attr] = Number


class Password:
    def __init__(self):
            #Variable for global cooldown game
        self.GlobalCooldown = 0
            #Variable to check if game has started/in progress, either True or False.
        self.Started = False
            #Start timer.
        self.StartedTime = False
            #Queue timer.
        self.QueueTime = False
            #Variable to check if queue is enabled. (True or False)
        self.Queue = False
            #List of users who joined the queue/game
        self.Joined = []
            #The actual password to guess. (4 letter string)
        self.Password = False
            #Encrypted password to display in chat. Gets updated when user guesses a positional
            #character. Example: **O*
        self.Encrypt = "****"
            #List of the password letters. Basically used as a reference to check letters in word.
        self.List = []
            #Dictionary to track guessed positional characters + viewers. 1 = character1, 2 = character2 etc.
            #It then sets the values to the usernames who guessed them.
            #In the "Points" function it then flips this dictionary for an accurate reading which users guessed
            #positional characters, and how many.
        self.Position = {"1": False, "2": False, "3": False, "4": False}
        self.Guesses = ["", "", "", "", ""]
        #self.Guesses = [{"Color": "Found", "String": ""}, {"Color": "Found", "String": ""}, {"Color": "Found", "String": ""}, {"Color": "Found", "String": ""}, {"Color": "Found", "String": ""}]

    def Start(self):
        for viewer in self.Joined:
            User.Add(viewer)

        self.Password = Password.get_random_line(FourLetterWords).strip()
        self.Encrypt, self.List, self.Position = "****", list(self.Password), {"1": False, "2": False, "3": False, "4": False}
        self.Guesses = ["", "", "", "", ""]
        Message = "[Password mini-game]: A 4 letter word has been selected! People who have joined the Queue can now start guessing. You have {} seconds. Goodluck!".format(MySet.GameTime)
        Parent.SendStreamMessage(Message)
        Parent.Log(ScriptName, "Password chosen for the Password mini-game: {}".format(self.Password))
        SendWebsocket("Start", self.Encrypt, False)

    #Function called when game ends. Either if there is a winner, or no winner. Variable "Wincondition" is used to check if there was a winner.
    def End(self, Wincondition, data):
        CurrentTime = round(self.StartedTime - time.time())
        self.GlobalCooldown, self.Started, self.Joined = time.time() + MySet.Cooldown, False, []
        Message = "The round has ended. The Password: [{}] has not been cracked. Better luck next time.".format(self.Password.upper())

        #Condition triggered when game has been won. Sets addictional variables and calls the Points function.
        if Wincondition:
            username = Parent.GetDisplayName(data.User)
            User.ChangeAttr(username, "Wins", 1)
            Message = "Password: [{}] has been succesfully guessed by {} with {} seconds remaining".format(self.Password, username, CurrentTime)
            FasterTime = round(MySet.GameTime - CurrentTime)
            if (User.PasswordDict[username]["Time"] == 0) or FasterTime < User.PasswordDict[username]["Time"]:
                User.ChangeAttr(username, "Time", FasterTime)
            Password.Points(data)
            SendWebsocket("Win", "", False)
            Parent.SendStreamMessage(Message)
            return
        User.Save()
        SendWebsocket("End", self.Encrypt, False)
        Parent.SendStreamMessage(Message)


    def Parse(self, data):
        username = Parent.GetDisplayName(data.User)
        if data.GetParam(0)[0] == data.GetParam(0)[1] == data.GetParam(0)[2] == data.GetParam(0)[3]:
            return
        #If word is exact to password, the person wins!
        if data.GetParam(0).lower() == self.Password:
            Password.End(True, data)
            return
        #Checking for letters. The first for loop checks if letters are in the same position.
        #For example if your password is "Crab" and person entered "Ceeb" this will then compare letter for letter for position.
        #So it will output that it has found C AND B in the same place.
        PositionalFound = 0
        FoundLetters = 0
        ListParse = []
        PositionalLetters = []
        for i, letter in enumerate(self.Password):
            if self.Position[str(i + 1)] == False:
                if letter == data.GetParam(0)[i]:
                    x = list(self.Encrypt)
                    x[i] = letter.upper()
                    self.Encrypt, self.Position[str(i + 1)] = "".join(x), username
                    PositionalFound += 1
                    User.ChangeAttr(username, "Guesses", 1)
                    self.List[i] = "*"
                    PositionalLetters.append(letter)
            else:
                continue
        #After we've parsed all letters in the same place. We parse them again, but this time we check if any letter is
        #in the Password. Position doesn't matter here.
        PasswordListCopy = self.List[:]
        for DiffLetter in data.GetParam(0):
            for i, value in enumerate(PasswordListCopy):
                if DiffLetter == value:
                    FoundLetters += 1
                    PasswordListCopy.pop(i)
                    break

        if FoundLetters > 0:
            if FoundLetters == 1:
                Multiple = "letter"
            else:
                Multiple = "letters"
            tempDict = {"Color": "Found", "String": "{}: guess [{}] - {} {} found".format(username, data.GetParam(0), FoundLetters, Multiple)}
            ListParse.append(tempDict)

        if PositionalFound > 0:
            if PositionalFound == 1:
                Multiple = "letter"
            else:
                Multiple = "letters"
            tempDict = {"Color": "Positional", "String": "{}: Found the correct position of {} - {}".format(username, Multiple, "-".join(PositionalLetters))}
            ListParse.append(tempDict)
        if ListParse:
            Password.ParseWebSocket(ListParse)


    #Function for leaderboard. It extracts all data from the UserDict data, then compares data against eachother.
    def LeaderBoard(self):
        if User.PasswordDict:
            Win, Guess, Fastest = 0, 0, 10000000
            for key in User.PasswordDict:
                if Win <= User.PasswordDict[key]["Wins"]:
                    WinData = key
                    Win = User.PasswordDict[key]["Wins"]
                if Guess <= User.PasswordDict[key]["Guesses"]:
                    GuessData = key
                    Guess = User.PasswordDict[key]["Guesses"]
                if Fastest >= User.PasswordDict[key]["Time"]:
                    FastestData = key
                    Fastest = User.PasswordDict[key]["Time"]

            if Win == 0:
                WinMessage = "Most Passwords cracked: [No one]"
            else:
                WinMessage = "Most Passwords cracked: [{} with {} passwords]".format(WinData, Win)
            if Guess == 0:
                GuessMessage = "Most letters guessed: [No one]"
            else:
                GuessMessage = "Most letters guessed: [{} with {} guessed]".format(GuessData, Guess)
            if Fastest == 0:
                TimeMessage = "Fastest Password cracked: [No one]"
            else:
                TimeMessage = "Fastest password cracked: [{} with time: {}]".format(FastestData, Fastest)

            if MySet.LeaderboardOverlay:
                if self.Started or self.Queue:
                    Message = "[Password Mini-game]: {} {} {}".format(WinMessage, GuessMessage, TimeMessage)
                else:
                    tempDict = [{"Color": "PositionalColor", "String": WinMessage}, {"Color": "GuessColor", "String": GuessMessage}, {"Color": "PositionalColor", "String": TimeMessage}, "", ""]
                    SendWebsocket("Leaderboard", "", tempDict)
                    return
            else:
                Message = "[Password Mini-game]: {} {} {}".format(WinMessage, GuessMessage, TimeMessage)
        else:
            Message = "[Password mini-game]: Could not display leaderboard because there aren't any entries."
        Parent.SendStreamMessage(Message)


    #Awarding points for winners and users who guessed positional characters.
    #Currently you can set the winners points and the positional is then calculated from that number.
    # 4 letters, so each positional is worth Winnerspoints / 4. It does NOT subtract from the winnerspoints though.
    def Points(self, data):
        User.Save()
        username = Parent.GetDisplayName(data.User)
        if not MySet.WinPoints <= 0:
            Quarterpoints = (MySet.WinPoints / 4)
        else:
            Quarterpoints = 0
        Message, MessageWin, flipped = "", None, {}

        for value, key in self.Position.iteritems():
            if key not in flipped:
                flipped[key] = [value]
            else:
                flipped[key].append(value)

        for key in flipped:
            if key == False:
                continue
            elif key == username:
                MessageWin = "and gets {} points for {} correct letters.".format((Quarterpoints * len(flipped[username])), len(flipped[username]))
                Parent.AddPoints(data.User, data.UserName, (MySet.WinPoints + (Quarterpoints * len(flipped[username]))))
            else:
                Message = "{}{} gets {} points for {} letters ".format(Message, username, (Quarterpoints * len(flipped[key]), len(flipped[key])))
                Parent.AddPoints(key.lower(), key, int(Quarterpoints * len(flipped[key])))

        if MessageWin:
            Message = "[Password mini-game]: {} gains {} points for winning {} {}".format(username, MySet.WinPoints, MessageWin, Message)
            Parent.SendStreamMessage(Message)
        else:
            Message = "[Password mini-game]: {} gains {} points for cracking the Password!".format(username, MySet.WinPoints)
            Parent.SendStreamMessage(Message)

    #Function to pull a word from textfile. This function ensures best grabbing of random word, as it goes to a random byte size and then grabs the next line.
    #To prevent the entire textfile being loaded into memory. I definitely didn't steal this from StackOverFlow.
    def get_random_line(self, file_name):
        total_bytes = os.stat(file_name).st_size
        random_point = random.randint(0, total_bytes)
        file = open(file_name)
        file.seek(random_point)
        file.readline() # skip this line to clear the partial line
        return file.readline()

    def ParseWebSocket(self, ListParse):
        for String in ListParse:
            Parent.Log(ScriptName, "This is the string: {}".format(String))
            Parent.Log(ScriptName, "Self.Guesses: {}".format(str(self.Guesses)))
            count = 0
            for value in self.Guesses:
                if value == "":
                    self.Guesses[count] = String
                    Parent.Log(ScriptName, "Adding to self.Guesses: {}".format(String))
                    count += 1
                    break
                count += 1
            else:
                self.Guesses.insert(0, String)
                self.Guesses.pop(5)
        SendWebsocket("Start", self.Encrypt, self.Guesses)


#---------------------------------------
# [Required] functions
#---------------------------------------

def Init():
    """data on Load, required function"""
    global MySet, Password, User
    MySet = Settings(settingsFile)
    Password = Password()
    User = User()
    # Load in saved settings
    MySet.SaveSettings(settingsFile)
    User.Load()
    # End of Init
    return

def Execute(data):
    if data.IsChatMessage:
        username = Parent.GetDisplayName(data.User)
        if Password.Started and username in Password.Joined and len(data.GetParam(0)) == 4 and data.GetParam(1) == "":
            Password.Parse(data)
            return

        if data.GetParam(0) == MySet.PrefixCommand:

          #PASSWORD START command
            if data.GetParam(1).lower() == "start":
                Time = time.time()
                if Time > Password.GlobalCooldown:
                    if Password.Started:
                        Message = "[Password mini-game]: There is already a game in progress."
                    elif Password.Queue:
                        Message = "[Password mini-game]: There is already a game in progress. Type {} <join> to join the Password mini-game!".format(MySet.PrefixCommand)
                    else:
                        Password.Queue = True
                        Password.QueueTime = MySet.QueueTime + time.time()
                        Message = "[Password mini-game]: Queue has started. Type {} <join> to join the Password mini-game!".format(MySet.PrefixCommand)
                        SendWebsocket("None", "", False)
                else:
                    newTime = Password.GlobalCooldown - Time
                    Message = "[Password mini-game]: Game is on cooldown for {} more seconds".format(int(newTime))

            #JOIN QUEUE command
            elif data.GetParam(1).lower() == "join":
                if Password.Started:
                    Message = "[Password mini-game]: There is already a game in progress."

                elif Password.Queue:
                    if username in Password.Joined:
                        return
                    Message = "[Password mini-game]: {} has joined this round of Password".format(username)
                    Password.Joined.append(username)

                elif not Password.Queue and not Password.Started:
                    Message = "[Password mini-game]: There is no game of Password in progress. Type {} start, to start a round of Password!".format(MySet.PrefixCommand)

            #RULES command
            elif data.GetParam(1).lower() == "rules":
                Message = "[Password mini-game]: The rules are as follows: I will pick a 4 letter word and encrypt it. You as a user will try and crack this code by typing a 4 letter word, If any letters are in the word (or in the correct position) the password will update and let you know. Goodluck!"

            #LEADERBOARD command
            elif data.GetParam(1).lower() == "leaderboard":
                Password.LeaderBoard()
                return
            else:
                Message = "[Password minigame]: Type {} <rules> for the rules, or {} <start> to start the mini-game".format(MySet.PrefixCommand, MySet.PrefixCommand)
            Parent.SendStreamMessage(Message)


def Tick():
    #Checking timer for game-Queue duration.
    if Password.Queue:
        currentTime = time.time()
        if currentTime > Password.QueueTime:
            if not len(Password.Joined) < MySet.MinUsers:
                Password.Queue, Password.Started, Password.StartedTime = False, True, currentTime + MySet.GameTime
                Message = "[Password mini-game]: Queue has ended!"
                Parent.SendStreamMessage(Message)
                Password.Start()
            else:
                Message = "[Password mini-game]: Game has ended because not enough people joined the queue."
                Parent.SendStreamMessage(Message)
                SendWebsocket("NoUsers", "", False)
                Password.Queue = False
                return
    """Checking timer for the game-round duration."""
    if Password.Started:
        currentTime = time.time()
        if currentTime > Password.StartedTime:
            Password.End(False, data=None)




#---------------------------------------
# [Required] API functions
#---------------------------------------

def openreadme():
    os.startfile(ReadMe)

#---------------------------------------
# Settings functions
#---------------------------------------

def ReloadSettings(jsondata):
    """Reload settings on Save"""
    # Reload saved settings
    MySet.ReloadSettings(jsondata)
    # End of ReloadSettings

def SaveSettings(self, settingsFile):
    """Save settings to files (json and js)"""
    with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
        json.dump(self.__dict__, f, encoding='utf-8-sig')
    with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
        f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig')))
    return

#!/usr/bin/python

import urllib2
import re
import datetime
import smtplib
from email.mime.text import MIMEText

def notifyUser(message):
    gmailLoginFile = open("gmailLogin.txt", "r")
    gmail_user = gmailLoginFile.readline().rstrip()
    gmail_pwd = gmailLoginFile.readline().rstrip()

    phoneNumberFile = open("phoneNumbers.txt", "r")
    phoneNumbers = []
    for number in phoneNumberFile:
        phoneNumbers.append(number.rstrip())

    dt = datetime.datetime.now()
    dateString = dt.strftime("%a %b %d, %Y %I:%M %p")

    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user, gmail_pwd)
    for number in phoneNumbers:
        header = 'To:' + number + '\n' + 'From: ' + gmail_user + '\n'
        msg = header + '\n' + dateString + "\n" + message + "\nhttps://www.jeopardy.com/tickets"
        smtpserver.sendmail(gmail_user, number, msg)
    smtpserver.close()


# get the html from the jeopardy ticket webpage
response = urllib2.urlopen("https://www.jeopardy.com/tickets")
html = response.read()

# search for section of webpage containing ticket availability
parsedMatch = re.search(r"<form class=\"requesttickets\".*</form>", html, re.DOTALL)

# check to see if the section even exists on webpage
if parsedMatch:
    parsedHtml = html[parsedMatch.start():parsedMatch.end()]
# if not, notify the user
else:
    notifyUser("This section did not appear in the html. Fix program.")

# search section for message of no ticket availability
noTicketMatch = re.search(r"There are no tapings scheduled at this time", parsedHtml)

# if message appears, notify user that no ticket is available
if not noTicketMatch:
    notifyUser("Tickets are available. Check website.")

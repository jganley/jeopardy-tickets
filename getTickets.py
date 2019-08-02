#!/usr/bin/env python3

import sys, os, datetime, urllib.request, smtplib, logging
from typing import List
from bs4 import BeautifulSoup
from dotenv import load_dotenv


def alreadySentText() -> bool:
    '''Check if this script has already sent a text today'''

    today = datetime.datetime.today()

    if not os.path.exists(os.path.dirname(sys.argv[0]) + '/AppData/execution_log.txt'):
        with open( os.path.dirname(sys.argv[0]) + '/AppData/execution_log.txt', 'w'): pass

    with open(os.path.dirname(sys.argv[0]) + '/AppData/execution_log.txt', 'r+') as f:
        if f.readline() == today.strftime('%m%d%Y'):
            return True

    return False


def storeSentText() -> None:
    '''Record in application data that we sent a text today'''

    today = datetime.datetime.today()

    with open(os.path.dirname(sys.argv[0]) + '/AppData/execution_log.txt', 'w+') as f:
        f.write(today.strftime('%m%d%Y'))


def requestPage(url: str):
    '''Send a GET request to the jeopardy website'''

    return urllib.request.urlopen(url)


def parseWebpage(html) -> List[str]:
    '''Use BeautifulSoup to parse the webpage for available tickets'''

    soup = BeautifulSoup(html, 'lxml')
    available = soup.find(class_='showtimes form-select required form-control')

    if available:
        return list(map(lambda x: x.get_text(), available.findAll('option')))

    return []


def sendTexts(message: str) -> None:
    '''Uses smtplib to send text to phone numbers'''

    gmail_user = os.getenv('JSERVE_USERNAME')
    gmail_pwd = os.getenv('JSERVE_PASSWORD')

    phoneNumberFile = open(os.path.dirname(sys.argv[0]) + "/AppData/phone_numbers.txt", "r")
    phoneNumbers = []
    for number in phoneNumberFile:
        phoneNumbers.append(number.rstrip())

    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user, gmail_pwd)
    for number in phoneNumbers:
        header = 'To:' + number + '\n' + 'From: ' + gmail_user + '\n'
        msg = header + '\n' + message
        smtpserver.sendmail(gmail_user, number, msg)
    smtpserver.close()


def main():
    # set logging variables
    logging.basicConfig(filename = os.path.dirname(sys.argv[0]) + '/AppData/app.log',
                        level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt = '%b %d %Y (%I:%M %p)')

    # check if a text has already been sent today
    if alreadySentText():
        logging.info('Already sent a text today.')
        sys.exit()

    # load the environment variables
    load_dotenv()

    # request the jeopardy ticket page
    html = requestPage("https://www.jeopardy.com/tickets")

    # parse the web page and return list of available ticket times
    tickets = parseWebpage(html)

    # send email if tickets are available
    if tickets:
        logging.info('Sending text right now.')

        message = "Jeopardy tickets are available!\n\n" + \
                  "\n".join(tickets[1:]) + "\n\n" + \
                  "https://www.jeopardy.com/tickets"

        if len(message) > 150:
            message = "Jeopardy tickets are available!\n\n" + \
                      "Too many dates to fit in one text :-(\n\n" + \
                      "https://www.jeopardy.com/tickets"

        sendTexts(message)
        storeSentText()

    else:
        logging.info('No tickets available right now.')


if __name__ == "__main__":
    main()

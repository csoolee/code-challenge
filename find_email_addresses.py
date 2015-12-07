"""
*************************
File : find_email_addresses.py

Author : Chris Lee

Date : 12-07-15

Program to take an internet domain name and print out a list of email addresses
that were found on the website. It should find email addresses on any discoversble
page of the website, not just the home page

Python version: 3.4

Libraries used: BeautifulSoup (pip install beautifulsoup4)

Tools used : Pyqt - installed using windows binary on website
            PyQt4-4.11.4-gpl-Py3.4-Qt4.8.7-x32
*************************
"""

#!/usr/bin/python
from bs4 import BeautifulSoup
from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.QtWebKit import *  
from urllib.request import urlopen

import urllib.parse as urlparse
import sys
import re 

# using set for easier membership testing, prevent duplicates from showing up
toBeVisited = set()
visitedPages = set()
emails = set()

# using PyQt4 to render javascript for a given page and return as html
app = QApplication(sys.argv)

def loadPage(url):
      page = QWebPage()
      loop = QEventLoop() # Create event loop
      page.mainFrame().loadFinished.connect(loop.quit) # Connect loadFinished to loop quit
      page.mainFrame().load(QUrl(url))
      loop.exec_() # Run event loop, it will end on loadFinished
      return page.mainFrame().toHtml()

def main():
    if (len(sys.argv) > 1):
        url = sys.argv[1]
    else:
        print("No url argument provided!")
        return
    # ensure url has scheme provided, if not, tack on "http://"
    url = correct_url(url)
    toBeVisited.add(url)
    # assume that the argument passed is the domain 
    domainName = url

    # main search loop
    print("Searching for emails...")
    while (len(toBeVisited) > 0):
        urlToBeVisited = toBeVisited.pop() # pop off one url that we want to visit, load it
        visitedPages.add(urlToBeVisited) # add it to set of visited urls so we don't revisit it
        html = loadPage(urlToBeVisited)     # load url with javascript rendered using PyQt library
        get_links(html, domainName) # find any new links to other pages on this domain 
        find_emails(html) # search html for any emails

    # print found emails
    print("Found " + str(len(emails)) + " emails:")
    for email in emails:
        print(email)

def correct_url(url):
    if (not url.startswith("http://") and not url.startswith("https://")):
        url = "http://" + url
    return url

# function using regex to match to emails in a string and returns them in a list
def match_emails(string):
    # email address must be of format : [anyChars]+@[anyChars]+.[anyChars]+
    return re.findall(r'[a-zA-Z0-9_]+@[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+',string)

def find_emails(content):
    foundEmails = match_emails(content)
    emails.update(foundEmails)

# searches webpage for links to other pages on website
def get_links(content, domainName):
    soup = BeautifulSoup(content, "html.parser")

    # use beautiful soup to parse html text for href links
    for tag in soup.findAll('a', href = True): # look for a tag
        raw = tag['href']
        hostName = urlparse.urlparse(raw).hostname
        pathName = urlparse.urlparse(raw).path
        if hostName is None:
            newurl = domainName + str(pathName)
        else:
            newurl = "http://" + str(hostName) + str(pathName)
        # assume that if hostname is not found, we have a link to another page on the same domain
        if hostName is None and newurl not in visitedPages:
            newurl = domainName + pathName
            toBeVisited.add(newurl)
        # not sure if we need this case?
        #if ()

if __name__ == "__main__":
    main()

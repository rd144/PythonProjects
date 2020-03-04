"""
Created by Ross Dingwall. JobWatch.py is a WebScraper that takes in a config and searches the url's contained in it for
user determined terms.

Long Term Goals:

    1 - Make and maintain a SQL database from the code itself
    2 - Check if a Job posting's status has been updated
    3 - Email a provided user

To do this, place the functionality into a class that can be called from other scripts.

#TODO - Parameterise and Functionalise
#TODO - Test on multiple URL's
#TODO - Stress Test on incorrect parameters
#TODO - Make a SQL Database and maintain it from within the code.
#TODO - Send Email if Job Updated.
"""

import requests
from bs4 import BeautifulSoup

def url_checker(url,watch_list,findall_name,findall_attribs=None):
    """
    Checks the URL provided using the parameters provided.

    TODO - Split up into sub-functions

    :param url: 
    :param watch_list:
    :param findall_name:
    :param findall_attribs:
    :return:
    """

    response = requests.get(url)

    soup = BeautifulSoup(response.text,'html.parser')
    results = soup.find_all(findall_name,findall_attribs)

    results_found = []

    for result in results:
        if result.text in watch_list:
            print("Found {post} at {url}".format(post=result.text,url=url))
            results_found.append(result.text)

    print("Found {count} results".format(count=len(results_found)))

    if len(results_found) != 0:
        return True
    else:
        return False

url_checker(
    url = "https://jobs.lever.co/kabam",
    findall_name = "h5",
    watch_list=[
        "Game data Analyst"
    ],
    findall_attribs = {"data-qa":"posting-name"}
)
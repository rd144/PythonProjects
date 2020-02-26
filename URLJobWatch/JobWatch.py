import requests
from bs4 import BeautifulSoup

def url_checker(url,watch_list,findall_name,findall_attribs=None):

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
from requests import get
from bs4 import BeautifulSoup

def download_file(url,filename):
    r = get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return filename

def find_and_download_video(soup,download_prefix):

    for index,video in enumerate(soup.find_all(id="video_holder")):
        print(f"Attempting Download of Video {index + 1}")

        postfix = video.find("iframe")["src"].split("/")[-1]
        url = f"{download_prefix}{postfix}"

        base_response = get(url)
        base_soup = BeautifulSoup(base_response.text, parser='html.parser', features='lxml')
        name = base_soup.find(property="og:title")["content"]
        print(f"{name}")

        download_url = base_soup.find(property="og:video")["content"]
        if name.split(".")[-1] != "mp4":
            name = name+".mp4"

        download_file(download_url, name)
        print(f"{name} downloaded")

# html_path = r"C:\Users\Ross\Downloads\12 of the best Christmas adverts ever, from ‘Mrs Claus’ to ‘The Man on The Moon’ _ The Independent _ The Independent.html"
# with open(html_path, 'r') as file:
#     soup = BeautifulSoup(file.read(), parser='html.parser', features='lxml')


response = get(r"https://www.youtube.com/playlist?list=PLC_T4reWfHDzGrjpEAwdColR8zgDA3aMm")
soup = BeautifulSoup(response.text, parser='html.parser', features='lxml')
print(soup)


prefix = r"http://cdn.jwplayer.com/players/"

print("Starting Download")

find_and_download_video(soup,prefix)

print("Download Complete")
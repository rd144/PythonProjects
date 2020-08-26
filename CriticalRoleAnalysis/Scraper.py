from bs4 import BeautifulSoup
from requests import get
import json


fuzzy_link = 'https://kryogenix.org/crsearch/html/{link}'


transcripts_link = fuzzy_link.format(link='index.html')
response = get(transcripts_link)
soup = BeautifulSoup(response.text,parser='html.parser',features='lxml')

results = soup.findAll(
    lambda tag:tag.name=="li" and "campaign" in tag.text.lower() and not tag.find('span',class_='unprocessed')
)

episode_record = {}

for result in results:
    episode_title = result.text
    print("Examining Episode {title}".format(title=episode_title))

    episode_link = result.a['href']
    new_page = fuzzy_link.format(link=episode_link)
    new_response = get(new_page)
    episode_soup = BeautifulSoup(new_response.text,parser='html.parser',features='lxml')

    lines = episode_soup.find('div',id='lines')
    lines = lines.findAll()

    speaker = None
    speaker_record = {}
    text_store = []

    for line in lines:
        if line.name == 'dt':
            if text_store and speaker:
                if speaker in speaker_record:
                    key = max(speaker_record[speaker].keys()) + 1
                else:
                    speaker_record[speaker] = {}
                    key = 1
                speaker_record[speaker][key] = " ".join(text_store)
            speaker = line.strong.text.title()
            text_store = []
        elif line.name == 'dd':
            text_store.append(line.text)

    episode_record[episode_title] = speaker_record

    print("Examination Complete")

print("All Episodes Examined")

with open('C:\\Users\\Ross\\Desktop\\GIT\\PythonProjects\\CriticalRoleAnalysis\\CriticalRoleSpokenRecordsUnclean.json','w') as file:
    json.dump(episode_record,file)
    quit()

from bs4 import BeautifulSoup
import re
from requests import get
import json
from datetime import datetime

class CriticalRoleScraper():

    def __init__(self):

        self.person_focus_list = [
            "Matt"
            , "Taliesin"
            , "Laura"
            , "Marisha"
            , "Liam"
            , "Sam"
            , "Ashley"
            , "Travis"
        ]

        self.fuzzy_link = 'https://kryogenix.org/crsearch/html/{link}'
        transcripts_link = self.fuzzy_link.format(link='index.html')
        base_response = get(transcripts_link)

        self.base_soup = BeautifulSoup(base_response.text,parser='html.parser',features='lxml')

    def episode_analysis(self):

        self.episode_record = {}

        results = self.base_soup.findAll(
            lambda tag: tag.name == "li" and "campaign" in tag.text.lower() and not tag.find('span',class_='unprocessed')
        )

        for result in results:
            episode_title = result.text
            print("Examining Episode {title}".format(title=episode_title))

            episode_link = result.a['href']
            new_page = self.fuzzy_link.format(link=episode_link)
            new_response = get(new_page)
            episode_soup = BeautifulSoup(new_response.text, parser='html.parser', features='lxml')

            lines = episode_soup.find('div', id='lines')
            lines = lines.findAll()

            speaker = None
            speaker_record = {}
            text_store = []
            text_store_flag = False

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
                    if speaker in self.person_focus_list:
                        text_store_flag = True
                    else:
                        text_store_flag = False
                    text_store = []

                elif line.name == 'dd':
                    nopunctuation = []
                    words = line.text.split()
                    for word in words:
                        # Remove Contractions 's 've 'd etc
                        word = word.split("'")[0]
                        # Replace Ampersand with word "and"
                        word = word.replace("&","and")
                        # Remove all punctuation and Digits except hyphenation
                        word = re.sub("(?=\W|\d)[^-]","",word)

                        if all(ord(char) < 128 for char in word):
                            nopunctuation.append(word.lower().strip())

                    if text_store_flag:
                        text_store.append(" ".join(nopunctuation))

            self.episode_record[episode_title] = speaker_record

            print("Examination Complete")

        print("All Episodes Examined")

def main():

    start = datetime.utcnow()

    run = CriticalRoleScraper()
    run.episode_analysis()

    with open('Outputs\\JSON\\CriticalRoleSpokenRecords.json','w') as file:
        json.dump(run.episode_record,file,indent=2)

    time = (datetime.utcnow() - start).total_seconds()
    print("Code Complete in {0}".format(time))

if __name__ == '__main__':
    main()

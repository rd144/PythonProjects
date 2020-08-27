import json
from nltk.corpus import stopwords
import pandas
from datetime import datetime


class CriticalRoleAnalysis():

    def __init__(self):

        self.start = datetime.utcnow()

        with open('Outputs/JSON/CriticalRoleSpokenRecords.json', 'r') as file:
            self.source_data = json.load(file)

        add_stops = ['said']
        self.stops = stopwords.words('english')
        self.stops.extend(add_stops)

        self.word_count_dict = {}
        self.full_df = pandas.DataFrame()
        self.limited_df = pandas.DataFrame()

        print("Initialised in {time}s since code start".format(time=(datetime.utcnow()-self.start).total_seconds()))

    def word_count_extraction(self):

        for episode in self.source_data:
            print("Extracting Word Counts for Episode: {title}".format(title=episode))
            spoken_record = self.source_data[episode]

            for person in spoken_record:
                if person not in self.word_count_dict:
                    self.word_count_dict[person] = {}
                spoken_sentences = spoken_record[person]
                for sentence_number in spoken_sentences:
                    sentence = spoken_sentences[sentence_number]
                    words = sentence.split()

                    for word in words:
                        word = word.lower().strip()
                        if word:
                            if word in self.word_count_dict[person] and word not in self.stops:
                                self.word_count_dict[person][word] += 1
                            else:
                                self.word_count_dict[person][word] = 1

        print("Word Count Extraction completed in {time}s since code start".format(time=(datetime.utcnow() - self.start).total_seconds()))

    def dataframe_translation(self):

        for person in self.word_count_dict:

            person_df = pandas.DataFrame(self.word_count_dict[person].items(), columns=["Word", "Count"])
            person_df["Person"] = person
            person_df["Normalized Percentage"] = person_df["Count"]/sum(person_df["Count"])

            self.full_df = self.full_df.append(person_df,ignore_index=True)

            person_df = person_df.sort_values(
                by="Normalized Percentage", ascending = False
            ).head(100)
            person_df["Normalized Percentage"] = person_df["Count"] / sum(person_df["Count"])

            self.limited_df = self.limited_df.append(person_df)

        print("DataFrame Translation completed in {time}s since code start".format(time=(datetime.utcnow() - self.start).total_seconds()))


    def aggregate_and_write(self):


        combined_df = self.full_df.groupby(['Word'])['Count'].agg('sum').reset_index()
        combined_df["Normalized Percentage"] = combined_df["Count"] / sum(combined_df["Count"])

        combined_df = combined_df.sort_values(
            by="Normalized Percentage", ascending=False
        ).head(500)
        combined_df["Normalized Percentage"] = combined_df["Count"] / sum(combined_df["Count"])

        print("Aggregation completed in {time}s since code start".format(time=(datetime.utcnow() - self.start).total_seconds()))

        self.limited_df.to_excel('Outputs\\Excel\\CriticalRoleSpokenWordsFull.xlsx', index=False)
        combined_df.to_excel('Outputs\\Excel\\CriticalRoleSpokenWordsCombined.xlsx', index=False)

        print("Dataframe Export to Excel completed in {time}s since code start".format(time=(datetime.utcnow() - self.start).total_seconds()))


run = CriticalRoleAnalysis()
run.word_count_extraction()
run.dataframe_translation()
run.aggregate_and_write()
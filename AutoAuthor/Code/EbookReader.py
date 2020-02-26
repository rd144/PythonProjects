from ebooklib import epub
import bs4

import json
import pandas
from csv import QUOTE_ALL
import os

import re
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from datetime import datetime

config_path = 'C:\\Users\\Ross\\Desktop\\Python Projects\\AutoAuthor\\Config.json'
output_directory = 'C:\\Users\\Ross\\Desktop\\Python Projects\\AutoAuthor\\'
config_file = open(config_path,'r')
config = json.load(config_file)
config_file.close()

def book_reader(path,chapter_flag,author,language="english"):

    book = epub.read_epub(path)
    word_dict = {}
    sentence_df = pandas.DataFrame()
    add_stops = ['said']
    stops = stopwords.words(language.lower())
    stops.extend(add_stops)

    def word_counter(word_dict,word_list):

        for word in word_list:
            word = word.lower().strip() 
            if word:
                if word in word_dict and word not in stops:
                    word_dict[word] += 1
                else:
                    word_dict[word] = 1

        return word_dict

    def chapter_process(item,sentence_df,word_dict):
        punctuation = "!\"#$%&()*+,-./:;<=>?@[\]^_`{|}~“”—…"

        chapter = bs4.BeautifulSoup(item.get_content(), 'html.parser')
        text_list = chapter.find_all('p')
        for index,line in enumerate(text_list):

            line = line.text
            sentence_list = sent_tokenize(line)
            nopunctuation = "".join([char for char in line if char not in punctuation])
            word_list = nopunctuation.split()

            if sentence_list:
                for sentence in sentence_list:
                    sentence_df = sentence_df.append(
                        {
                            "Author": author,
                            "Sentence": sentence
                        }, ignore_index=True
                    )
            if word_list:
                word_dict = word_counter(word_dict, word_list)

            if index % 25 == 0 and index != 0:
                print("Processed {line_count} lines".format(line_count=index))

        return sentence_df, word_dict

    chapter_count = 0
    for index,item in enumerate(book.get_items_of_media_type("application/xhtml+xml")):
        if chapter_flag in str(item):
            chapter_count += 1
            print("Processing chapter {number}".format(number=chapter_count))
            sentence_df, word_dict = chapter_process(item, sentence_df, word_dict)
            print("Chapter Processing Complete")

    return sentence_df,word_dict

def main():

    start_time = datetime.utcnow()

    final_sentence_df = pandas.DataFrame()
    final_word_df = pandas.DataFrame()

    author_count = {}

    for file_path in config:
        book_name = os.path.basename(file_path).replace(".csv","")
        print("Processing {file} by {author}".format(file=book_name,author=config[file_path]["author"]))
        file_config = config[file_path]
        sentence_df,word_dict = book_reader(
            path = file_path,
            chapter_flag = file_config["chapter_flag"],
            author = file_config["author"]
        )

        word_df = pandas.DataFrame(word_dict.items(), columns=["Word", "Count"])
        word_df["Author"] = config[file_path]["author"]
        word_df["Book"] = book_name
        final_sentence_df = final_sentence_df.append(sentence_df,ignore_index=True)
        final_word_df = final_word_df.append(word_df,ignore_index=True)

        word_count = word_df["Count"].sum()
        sentence_count = len(sentence_df)

        if file_config["author"] in author_count:
            author_count[file_config["author"]]["Book Count"] += 1
            author_count[file_config["author"]]["Word Count"] += word_count
            author_count[file_config["author"]]["Sentence Count"] += sentence_count
        else:
            author_count[file_config["author"]] = {}
            author_count[file_config["author"]]["Book Count"] = 1
            author_count[file_config["author"]]["Word Count"] = word_count
            author_count[file_config["author"]]["Sentence Count"] = sentence_count

        print("Book Processing Complete")

    print(author_count.items())

    for author in author_count:
        print(author, author_count[author]["Book Count"], author_count[author]["Word Count"],
              author_count[author]["Sentence Count"])

    print("Code Compeleted in {time} seconds".format(
        time=(datetime.utcnow()-start_time).total_seconds()
    ))

    final_sentence_df.to_csv(output_directory + "FinalSentence.csv",quoting=QUOTE_ALL,sep="|",index=False)
    final_word_df.to_csv(output_directory + "FinalWords.csv",quoting=QUOTE_ALL,sep="|",index=False)

if __name__ == '__main__':
    main()

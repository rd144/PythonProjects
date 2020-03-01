from ebooklib import epub
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import bs4
import pandas
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from csv import QUOTE_ALL
from datetime import datetime
import glob
import os
import re

def config_builder(source_directory):
    """
    A function that builds a config for the EbookReader Class. It scans through a provided directory and for each
    epub file it finds, it parses the file and looks for the most frequent term used, once numerical values have been
    stripped away (chapter1,chapter2 etc. becomes chapter).
    :param source_directory: The directory containing the epub files. Must be structured such that the author's name is the
    :return:
    """

    def dict_key_value_extract(key_term, dict_object):

        if hasattr(dict_object, 'items'):
            for key, value in dict_object.items():
                if key == key_term:
                    yield value
                elif isinstance(value, dict):
                    for result in dict_key_value_extract(key_term, value):
                        yield result
                elif isinstance(value, list):
                    for item in value:
                        for result in dict_key_value_extract(key_term, item):
                            yield result

    def value_dive(object):

        while not isinstance(object,str):
            object = object[0]
        return object

    book_list = []
    non_num_patt = re.compile("[^\d]")
    output_dict = {}

    path_list = glob.iglob(source_directory+"/**/*",recursive=True)

    for file_path in path_list:

        if ".epub" in file_path and os.path.isfile(file_path):
            if os.path.basename(file_path) not in book_list:
                print("Processing {file}".format(file=os.path.basename(file_path)))
                book_list.append(os.path.basename(file_path))
                book = epub.read_epub(file_path)
                title = value_dive(list(dict_key_value_extract("title", book.metadata)))
                author = value_dive(list(dict_key_value_extract("creator", book.metadata)))

                term_count = {}
                for item in book.get_items_of_media_type("application/xhtml+xml"):
                    name = str(item).split(":")[1]
                    non_numerical = "".join(non_num_patt.findall(name))
                    if non_numerical in term_count:
                        term_count[non_numerical] += 1
                    else:
                        term_count[non_numerical] = 1
                term = max(term_count, key=term_count.get)

                output_dict[file_path] = {
                    "author" : author,
                    "title" : title,
                    "chapter_flag" : term
                }

    return output_dict

def book_reader(path,chapter_flag,author,language="english"):
    """
    This parameter takes the path of an epub file and extracts the text from it into a dataframe of sentences, and a
    dictionary containing each word and the frequency it occurs in the book
    :param path: Path to the epub file
    :param chapter_flag: The flag that the epub uses to identify chapters
    :param author: The author for the book
    :param language: The language the book is written in (defaults to english)
    :return sentence_df: A DataFrame object that contains the author and all the sentences used in the book
    :return word_dict: A dictionary object that contains all the words used in the book (as a key) and it's count
    """

    def word_counter(word_dict,word_list):
        """
        A subfunction for updating the word_dict object with the count of words in a given list of words
        :param word_dict: Existing word_dict object
        :param word_list: A list of words
        :return word_dict: Updated word_dict object
        """

        for word in word_list:
            word = word.lower().strip()
            if word:
                if word in word_dict and word not in stops:
                    word_dict[word] += 1
                else:
                    word_dict[word] = 1

        return word_dict

    def chapter_process(item,sentence_df,word_dict):
        """
        A sub function that takes an EpubHtml object that has been flagged as a chapter and uses BeautifulSoup to extract
        the text values and form them into the sentence_df and word_dict object
        :param item: Epubhtml Object, flagged as a chapter
        :param sentence_df: Existing sentence_df object to have the chapters information appended to
        :param word_dict: Existing word_dict object to have the chapters information appended to
        :return sentence_df: Updated sentence_df object containing the chapters information
        :return word_dict: Updated word_dict object containing the chapters information
        """

        chapter = bs4.BeautifulSoup(item.get_content(), 'html.parser')
        text_list = chapter.find_all('p')
        for index,line in enumerate(text_list):

            line = line.text
            sentence_list = sent_tokenize(line)
            nopunctuation = re.sub("(\W+|\d+)"," ",re.sub("(’|')","",line))
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

    book = epub.read_epub(path)
    word_dict = {}
    sentence_df = pandas.DataFrame()
    add_stops = ['said']
    stops = stopwords.words(language.lower())
    stops.extend(add_stops)

    chapter_count = 0
    for index,item in enumerate(book.get_items_of_media_type("application/xhtml+xml")):
        if chapter_flag in str(item):
            chapter_count += 1
            print("Processing chapter {number}".format(number=chapter_count))
            sentence_df, word_dict = chapter_process(item, sentence_df, word_dict)
            print("Chapter Processing Complete")

    return sentence_df,word_dict

def book_analysis(config):

    def normalise_word_df(dataframe):

        print("Normalizing the Word Dataframe")

        gb_columns = ["Author", "Word"]
        word_sum = dataframe.groupby(gb_columns)["Count"].sum().reset_index().rename(columns={"Count": "Word Count"})
        author_totals = dataframe.groupby(["Author"])["Count"].sum().reset_index().rename(columns={"Count": "Total Count"})
        normalized = word_sum.merge(author_totals, on="Author")
        normalized["Normalized Percentage"] = normalized["Word Count"] / normalized["Total Count"]

        print("Normalization complete")

        return normalized

    print("Extracting Book Information")

    final_sentence_df = pandas.DataFrame()
    final_word_df = pandas.DataFrame()

    for file_path in config:
        file_config = config[file_path]
        book_name = file_config["title"]
        author = file_config["author"]
        chapter_flag = file_config["chapter_flag"]

        print("Processing {file} by {author}".format(file=book_name, author=author))
        sentence_df, word_dict = book_reader(
            path = file_path,
            chapter_flag = chapter_flag,
            author = author
        )

        word_df = pandas.DataFrame(word_dict.items(), columns=["Word", "Count"])
        word_df["Author"] = author
        word_df["Book"] = book_name
        final_sentence_df = final_sentence_df.append(sentence_df, ignore_index=True)
        final_word_df = final_word_df.append(word_df, ignore_index=True)

        print("Book Processing Complete")
    final_word_df = normalise_word_df(final_word_df)
    print("Extraction Complete")
    return final_sentence_df, final_word_df

def word_cloud_creation(dataframe,key_column,value_column,title=None):

    dataframe =  dataframe[[key_column,value_column]]

    tuples = [tuple(x) for x in dataframe.values]
    wordcloud = WordCloud(background_color="white",max_words=200,width=3200, height=1600).generate_from_frequencies(dict(tuples))
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    if title:
        plt.title(title)
    return plt

def main(source_directory,output_directory):

    start_time = datetime.utcnow()
    config  = config_builder(source_directory)
    final_sentence_df, final_word_df = book_analysis(config)

    if not output_directory.endswith("\\"):
        output_directory = output_directory + "\\"

    print("Outputing Dataframes to {output_directory}".format(output_directory=output_directory))

    final_sentence_df.to_csv(output_directory + "FinalSentences.csv", sep="|", quoting=QUOTE_ALL, index=False)
    final_word_df.to_csv(output_directory + "FinalWords.csv", sep="|", quoting=QUOTE_ALL, index=False)

    print("DataFrame Output Complete")

    print("Creating Wordlouds for each author\nWord Clouds can be found in {output_directory}".format(output_directory=output_directory+"WordClouds"))

    for author in final_word_df["Author"].drop_duplicates():
        output_path = "{directory}WordClouds\\{author}.png".format(
            directory=output_directory,
            author=author
        )
        print("Creating Wordcloud for {author}".format(author=author))
        cloud = word_cloud_creation(
            dataframe=final_word_df[final_word_df["Author"] == author],
            key_column="Word",
            value_column="Normalized Percentage",
            title=author
        )

        cloud.savefig(output_path + "\\{filename}.png".format(filename=author))
        cloud.close()
    print("Word Cloud Creation Complete")

    print("Code Completed in {time} seconds".format(
        time=(datetime.utcnow() - start_time).total_seconds()
    ))

if __name__ == '__main__':

    main(
        source_directory = 'C:\\Users\\Ross\\Google Drive\\Calibre Library\\',
        output_directory = 'C:\\Users\\Ross\\Desktop\\GIT\\PythonProjects\\AutoAuthor\\Outputs'
    )

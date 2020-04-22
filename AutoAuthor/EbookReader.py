"""
Created by Ross Dingwall. EbookReader.py is a script to parse directories of epub files and return DataFrames containing
information regarding the word frequency and sentences used within those files.

Known Bugs:
    * Currently the code will see the author "John Smith" as different from "Smith, John". While a function could be put in place to resolve this. I believe it may lead to more issues, when a manual review of the data would resolve this swiftly. However, for very large DataSets, this bug may be better resolved automatically.

TODO:
    * Expand the code to work on Linux as well as Windows
    * Move import statements into the functions that use them to allow them to be properly called from outside the main
    * Create the output directory and it's structure if it's not already in place

"""

from ebooklib import epub
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import bs4
import pandas
from csv import QUOTE_ALL
from datetime import datetime
import glob
import os
import re
import argparse

def arguments():
    """
    Parses all the required arguments and returns them as the "args" object.
    Required Arguments include:

    1. source_directory - The directory that contains the Ebooks you wish analysed.
    2. output_directory - The directory you wish the results created.

    :return args: Namespace object containing the parsed value for the argument assigned to it's corresponding name
    :rtype args: class 'argparse.Namespace'
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--source_directory")
    parser.add_argument("--output_directory")

    args = parser.parse_args()

    return args

def config_builder(source_directory):
    """

    A function that builds a config for the book_analysis function. It scans through a provided directory and for each
    epub file it finds, it parses the file and looks for the most frequent term used, once numerical values have been
    stripped away (chapter1,chapter2 etc. becomes chapter).

    :param source_directory: The filepath for the base directory containing any and all epub files you want analysed.
    :type source_directory: class 'str'
    :return output_dict: A dictionary object that can be used as the config for the Book Analysis function. It contains a list of epub filepaths in the source directory, what author they are from, what the title is, and what term designates a chapter
    :rtype output_dict: class 'dict'

    """

    def dict_key_value_extract(key_term, dict_object):
        """
        A recursive sub-function used to find all instances of the key term provided in a nested dict object

        :param key_term: a string object you want to find as a value in the dict
        :param dict_object: a dictionary object (can be nested) which the code will find all instances of the key_term
        """

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
        """
        A sub-function for returning the left most string object in a dictionary/tuple/list of lists

        :param object: The object you want to retrieve the left-most object from
        :return object: The found string in the left most position
        """

        while not isinstance(object,str):
            object = object[0]
        return object

    # Setup initial objects to be used later in the code
    process_list = []
    non_num_patt = re.compile("[^\d]")
    output_dict = {}

    # Create an iterator for all the file paths in the source directory provided
    path_list = glob.iglob(source_directory+"/**/*",recursive=True)

    for file_path in path_list:

        if ".epub" in file_path and os.path.isfile(file_path):

            # Read the book and extract the Title and Author from the metadata
            book = epub.read_epub(file_path)
            title = value_dive(list(dict_key_value_extract("title", book.metadata)))
            author = value_dive(list(dict_key_value_extract("creator", book.metadata)))

            # Keep a list of the Authors and Titles processed, and check it, to minimise duplication
            if "_".join([author,title]) not in process_list:
                process_list.append("_".join([author,title]))
                print("Processing {file}".format(file=os.path.basename(file_path)))

                # For each term in the html of the file, take a count of it without numbers. If you take the most common
                # term you receive the chapter flag, as it's the most common item in an epub.

                term_count = {}
                for item in book.get_items_of_media_type("application/xhtml+xml"):
                    name = str(item).split(":")[1]
                    non_numerical = "".join(non_num_patt.findall(name))
                    if non_numerical in term_count:
                        term_count[non_numerical] += 1
                    else:
                        term_count[non_numerical] = 1
                term = max(term_count, key=term_count.get)

                # Add the created config for the file path to the dictionary
                output_dict[file_path] = {
                    "author" : author,
                    "title" : title,
                    "chapter_flag" : term
                }

    return output_dict

def supermakedir(directory,permission):

    if not os.path.isdir(directory):
        oldmask = os.umask(000)
        os.makedirs(directory,exist_ok=True,mode=permission)
        os.umask(oldmask)

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
    """

    A function which takes the config created by the config builder, iterates through all the stored filepaths and there
    details, and extracts information on each word, and sentence used by the author of the book. This information is stored
    in DataFrame objects, and the word DataFrame is normalised before being returned.

    :param config: The dictionary object config, created by config_builder (based on a source_directory)
    :type config: class 'dict'
    :return final_sentence_df: A DataFrame object containing each sentence the author wrote, and in what book they wrote it.
    :rtype final_sentence_df: class 'pandas.core.frame.DataFrame'
    :return final_word_df: A DataFrame object containing each word an author used, the total words the author used, and the normalised ratio of that word against all words used by the author for comparison against other authors.
    :rtype final_word_df: class 'pandas.core.frame.DataFrame'

    """

    def normalise_word_df(dataframe):
        """
        A sub-function for normalising a given DataFrame

        :param dataframe: The DataFrame object you wish to normalise
        :return normalized: The Normalized DataFrame object
        """
        #TODO - Add parameters to make this able to be used more generally
        print("Normalizing the Word Dataframe")

        gb_columns = ["Author", "Word"]
        word_sum = dataframe.groupby(gb_columns)["Count"].sum().reset_index().rename(columns={"Count": "Word Count"})
        author_totals = dataframe.groupby(["Author"])["Count"].sum().reset_index().rename(columns={"Count": "Total Count"})
        normalized = word_sum.merge(author_totals, on="Author")
        normalized["Normalized Percentage"] = normalized["Word Count"] / normalized["Total Count"]

        print("Normalization complete")

        return normalized

    print("Extracting Book Information")

    # Initialise the empty DataFrames
    final_sentence_df = pandas.DataFrame()
    final_word_df = pandas.DataFrame()

    for file_path in config:
        # Bring the config to the filepath Level and extract all useful information regarding the filepath from it
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

        # Change the word_dict (containing words and frequencies) into a DataFrame and add Author/Title details
        word_df = pandas.DataFrame(word_dict.items(), columns=["Word", "Count"])
        word_df["Author"] = author
        word_df["Book"] = book_name
        sentence_df["Book"] = book_name

        # Append the information for the Title to a final DataFrame containing all the information
        final_sentence_df = final_sentence_df.append(sentence_df, ignore_index=True)
        final_word_df = final_word_df.append(word_df, ignore_index=True)

        print("Book Processing Complete")

    # Normalise the final word_df object
    #TODO - If I perform analysis on the sentences the final_sentence_df will need to be normalised as well
    final_word_df = normalise_word_df(final_word_df)
    print("Extraction Complete")
    return final_sentence_df, final_word_df

def main(source_directory,output_directory):
    """
    The main function of the EbookReader code. This function runs all the others in order, first creating the config from
    the source directory, then analysing the contents of the files in the config, before outputing the raw data as csv's
    and wordclouds for each author to the provided output directory

    :param source_directory: The directory on your system containing all the epub files
    :param output_directory: The directory on your system you wish to place the outputs
    """

    start_time = datetime.utcnow()
    config = config_builder(source_directory)
    final_sentence_df, final_word_df = book_analysis(config)

    if not output_directory.endswith("\\"):
        output_directory = output_directory + "\\"

    print("Outputing Dataframes to {output_directory}".format(output_directory=output_directory))

    if not os.path.exists(output_directory):
        supermakedir(output_directory,0o775)

    final_sentence_df.to_csv(output_directory + "FinalSentences.csv", sep="|", quoting=QUOTE_ALL, index=False)
    final_word_df.to_csv(output_directory + "FinalWords.csv", sep="|", quoting=QUOTE_ALL, index=False)

    print("DataFrame Output Complete")

    print("Code Completed in {time} seconds".format(
        time=(datetime.utcnow() - start_time).total_seconds()
    ))

if __name__ == '__main__':

    args = arguments()
    main(
        source_directory = args.source_directory,
        output_directory = args.output_directory
    )

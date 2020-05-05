'''
The idea of this script is to create a Class that you can provide a Wikipedia link to and it will condense and return
the top "n" passages it thinks are key

This is mostly proof of concept to be attached to the AutoAuthor script upon completion.

run example:

python C:/Users/Ross/Desktop/GIT/PythonProjects/WikiCondense/WikiCondense.py --wiki_url "https://en.wikipedia.org/wiki/Darth_Vader" --summary_sentence_limit "5"
'''

import nltk
import requests
from bs4 import BeautifulSoup
import re
import heapq
import argparse

def url_info_extraction(wiki_url):

    response = requests.get(wiki_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    text_content = "".join([p.text for p in paragraphs])
    return text_content

def text_cleanup(text_content):

    text_content = re.sub('\[[0-9]*\]', ' ', text_content)
    text_content = re.sub('\s+', ' ', text_content)

    formatted_article_text = re.sub('[^a-zA-Z]', ' ', text_content)
    formatted_article_text = re.sub('\s+', ' ', formatted_article_text)

    return formatted_article_text,text_content

def word_processing(formatted_article_text):

    stopwords = nltk.corpus.stopwords.words('english')
    word_frequencies = {}
    for word in nltk.word_tokenize(formatted_article_text):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    maximum_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word] / maximum_frequency)

    return word_frequencies

def sentence_processing(text_content,word_frequencies):

    sentence_list = nltk.sent_tokenize(text_content)
    sentence_scores = {}
    sentence_order = {}
    for index, sent in enumerate(sentence_list):
        if sent not in sentence_order.keys():
            sentence_order[sent] = index
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word]
                else:
                    sentence_scores[sent] += word_frequencies[word]

    return sentence_order,sentence_scores

def arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument('--wiki_url',type=str)
    parser.add_argument('--summary_sentence_limit', type=int,default=10)
    args = parser.parse_args()

    return args

def main(wiki_url,summary_sentence_limit):

    text_content = url_info_extraction(wiki_url)
    formatted_article_text,text_content = text_cleanup(text_content)
    word_frequencies = word_processing(formatted_article_text)
    sentence_order,sentence_scores = sentence_processing(text_content,word_frequencies)

    summary = heapq.nlargest(summary_sentence_limit,sentence_scores,key=sentence_scores.get)
    summary = sorted(summary,key=sentence_order.get)

    for sent in summary:
        print(sentence_order[sent],sentence_scores[sent],sent)

if __name__ == '__main__':
    args = arguments()
    main(
        wiki_url=args.wiki_url,
        summary_sentence_limit=args.summary_sentence_limit
    )




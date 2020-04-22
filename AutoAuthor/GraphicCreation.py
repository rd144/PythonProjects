"""
Created by Ross Dingwall. GraphicCreation.py is a module containing all functions used to create graphics from varying
datasets.

"""
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def word_cloud_creation(dataframe,key_column,value_column,title=None):
    """

    A function for creating wordcloud objects based on a DataFrame and two column names
    (one for the key, and one for the values)

    :param dataframe: The Dataframe containing the WordCloud information
    :type dataframe: class 'pandas.core.frame.DataFrame'
    :param key_column: The name for the DataFrame column containing the words
    :type key_column: class 'str'
    :param value_column: The name for the DataFrame column containing the float value you wish to associate with the Words
    :type value_column: class 'str'
    :param title: Defaults to None, but if a Title is provided it will be added to the WordCloud
    :type title: class 'str'

    :return plt: plt object containing the wordcloud of the provided data
    :rtype plt: class 'matplotlib.figure.Figure'
    """

    dataframe =  dataframe[[key_column,value_column]]

    tuples = [tuple(x) for x in dataframe.values]
    wordcloud = WordCloud(background_color="white",max_words=200,width=3200, height=1600).generate_from_frequencies(dict(tuples))
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    if title:
        plt.title(title)
    return plt

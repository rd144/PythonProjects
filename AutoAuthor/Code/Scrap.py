import pandas
from csv import QUOTE_ALL
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image

input_path = "C:\\Users\\Ross\\Desktop\\GIT\\PythonProjects\\AutoAuthor\\Outputs\\FinalWords.csv"
output_path = "C:\\Users\\Ross\\Desktop\\GIT\\PythonProjects\\AutoAuthor\\Outputs\\WordClouds"
df = pandas.read_csv(input_path,sep="|",quoting=QUOTE_ALL)

def word_cloud(dataframe,key_column,value_column,title=None):

    dataframe =  dataframe[[key_column,value_column]]

    tuples = [tuple(x) for x in dataframe.values]
    wordcloud = WordCloud(background_color="white",max_words=200,width=3200, height=1600).generate_from_frequencies(dict(tuples))
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    if title:
        plt.title(title)
    return plt

for author in df["Author"].drop_duplicates():
    print("Creating Wordcloud for {author}".format(author=author))
    cloud = word_cloud(
        dataframe=df[df["Author"] == author],
        key_column="Word",
        value_column="Normalized Percentage",
        title=author
    )




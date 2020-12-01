import pytube
import re
import argparse

def playlist_scraper(url,output_directory):

    playlist = pytube.Playlist(url)

    playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")

    for video_url in playlist:
        video = pytube.YouTube(video_url)
        print("Downloading {0}".format(video.title))
        streams = video.streams.filter(file_extension="mp4",progressive=True)
        max_res = max([stream.resolution for stream in streams])
        stream = streams.filter(resolution=max_res)[0]
        stream.download(output_directory)
        print("Download Complete")

def arguments():

    args = argparse.ArgumentParser()
    args.add_argument("--url")
    args.add_argument("--output_directory")

    return args.parse_args()

def main():
    args = arguments()
    playlist_scraper(
        url=args.url
        ,output_directory = args.output_directory
    )

if __name__ == '__main__':
    main()
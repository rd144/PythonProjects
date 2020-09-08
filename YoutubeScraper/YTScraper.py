import pytube
import re
from datetime import datetime

playlist_url = 'https://www.youtube.com/playlist?list=PLui6Eyny-UzwxbWCWDbTzEwsZnnROBTIL'
dir_name = "30DaysOfYoga"
start = datetime.utcnow()

output_directory = "Outputs/{0}/{1}"

playlist = pytube.Playlist(playlist_url)

playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")

for video_url in playlist:
    video = pytube.YouTube(video_url)
    print("Downloading {0}".format(video.title))
    streams = video.streams.filter(file_extension="mp4",progressive=True)
    max_res = max([stream.resolution for stream in streams])
    stream = streams.filter(resolution=max_res)[0]
    stream.download(output_directory.format(dir_name,start.strftime('%Y-%M-%d')))
    print("Download Complete")
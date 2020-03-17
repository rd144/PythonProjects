import praw
import datetime

connection_details = {
    "client_id" : "vJy_s_GTnIJCTw",
    "client_secret" : "mhzTWdLQBn81ju3PgDWIwrwqCBs",
    "user_agent" : "WritingPrompt",
    "username" : "rd144",
    "password" : "5c00ter"
}

reddit = praw.Reddit(
    client_id=connection_details["client_id"],
    client_secret=connection_details["client_secret"],
    user_agent=connection_details["user_agent"],
    username=connection_details["username"],
    password=connection_details["password"]
)

subreddit = reddit.subreddit('WritingPrompts')

today = datetime.datetime.utcnow()
today = datetime.datetime(year=today.year,month=today.month,day=today.day)

last_week_start = today - datetime.timedelta(days=7)
last_week_end = last_week_start + datetime.timedelta(hours=23,minutes=59,seconds=59)

epoch = datetime.datetime(1970,1,1)
UTC_Start = (last_week_start - epoch).total_seconds()
UTC_End = (last_week_end - epoch).total_seconds()

for item in dir(subreddit):
    print(item)


class RedditEmailer():

    def __init__(self,reddit_config,email_config):

        self.reddit_config = reddit_config
        self.email_config = email_config

    def create_reddit_object(self):
        import praw

        reddit = praw.Reddit(
            client_id=self.reddit_config["client_id"],
            client_secret=self.reddit_config["client_secret"],
            user_agent=self.reddit_config["user_agent"],
            username=self.reddit_config["username"],
            password=self.reddit_config["password"]
        )

        return reddit

    def subreddit_list_scraper(self,reddit,subreddit,start_text=None,count=10):

        subreddit = reddit.subreddit(subreddit)
        submission_list = []

        for index,submission in enumerate(subreddit.top(limit=1000)):
            text = submission.title
            if start_text:
                if text.startswith(start_text):
                    submission_list.append(submission)
            else:
                submission_list.append(submission)

            if len(submission_list) >= count:
                break

        return submission_list

    def message_creation(self,submission_list,subject,removal_expressions=None):
        import re
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        email_message = MIMEMultipart("alternative")
        email_message["Subject"] = subject

        if removal_expressions:
            pattern_list = []
            for expression in removal_expressions:
                pattern_list.append(re.compile(expression))
        line_list = []
        for index, submission in enumerate(submission_list):
            message = submission.title
            if pattern_list:
                for expression in pattern_list:
                    message = expression.sub("", message)

            line = "{number}. {url}\nPost:{message}\n\n".format(
                number=index+1,
                url=submission.url,
                message=message
            )
            line_list.append(line)

        email_message.attach(
            MIMEText("".join(line_list),'plain','utf-8')
        )

        return email_message

    def send_emails(self,message):
        import smtplib

        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(
            user=self.email_config["fromEmail"],
            password=self.email_config["fromPassword"]
        )

        distribution_list = self.email_config["distributionList"]

        for toEmail in distribution_list:
            session.sendmail(
                msg=message.as_string(),
                to_addrs=toEmail,
                from_addr=self.email_config["fromEmail"]
            )

def arguments():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--subreddit")
    parser.add_argument("--config_path")
    parser.add_argument("--subject",default="PythonGeneratedEmail")
    parser.add_argument("--start_text",default=None)
    parser.add_argument("--count", default=10,type=int)

    return parser.parse_args()

def main(config_path,subreddit,start_text,count,subject):
    import json
    import datetime

    file = open(config_path)
    config = json.load(file)
    file.close()

    session = RedditEmailer(
        config["connection_details"],
        config["email_config"]
    )
    reddit = session.create_reddit_object()
    submission_list = session.subreddit_list_scraper(
        reddit=reddit,
        subreddit=subreddit,
        start_text = start_text,
        count=count
    )
    message = session.message_creation(
        submission_list = submission_list,
        subject="{subject} - {date}".format(
            subject=subject,
            date=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        ),
        removal_expressions=config["email_config"]["removalExpressions"]
    )
    session.send_emails(message)

if __name__ == '__main__':
    args = arguments()
    main(
        subreddit=args.subreddit, # e.g. all for r/all
        config_path=args.config_path, # Path to the config
        subject=args.subject, # Subject you want for the Email
        start_text=args.start_text, # Start text for the posts to filter by (i.e [WP] is the start of titles on r/WritingPrompts
        count=args.count # Number of responses you want to send
    )

"""
Created by Ross Dingwall - This module is used to scrape the top "n" posts of a subreddit and send them to a mailing list.
The intent behind this is to provide my partner with creative writing prompts whenever they require them.

TODO:
    * Splitting it into multiple classes 1 for emailing and one for reddit would allow for use in other scripts.
    * Add Functionality to look at more than just top comments (most controversial, hottest etc.)
    * Add functionality to look for an indefinite amount of comments (not limited to < 1000)
"""


class RedditEmailer():
    """
    :param reddit_config: A dictionary object containing the connection details required for connecting to Reddit. Including client_id, client_secret, user_agent, username, password
    :type reddit_config: class 'dict'
    :param email_config: A Dictionary object containing the connection details required for sending emails via gmail. Including fromEmail, fromPassword, distributionList, removalExpressions
    :type email_config: class 'dict'
    :param previous_posts_path: The path you wish to keep the previous posts collected by this script.
    :type previous_posts_path: class 'str'

    """

    def __init__(self,reddit_config,email_config,previous_posts_path):
        import os

        print('RedditEmailer Class Initiating')

        self.reddit_config = reddit_config
        self.email_config = email_config
        self.previous_posts_path = previous_posts_path
        print('Arguments saved to self')

        if os.path.isfile(previous_posts_path):
            print('Previous posts file found')
            file = open(previous_posts_path,'r',encoding='utf-8')
            self.previous_posts = [line.strip() for line in file]
            file.close()
            print('Previous posts loaded')
        else:
            print('Previous posts file found')
            file = open(previous_posts_path, 'w')
            self.previous_posts = []
            file.close()
            print('Previous posts file created at {path}'.format(path=previous_posts_path))

        print('Initiation Complete')

    def create_reddit_object(self):
        """
        Initialises and returns the reddit object using the parameters contained in the reddit_config saved to self

        :return reddit: Reddit object created by the praw library using the reddir config details passed to the RedditEmailer Class
        :rtype reddit: class 'praw.reddit.Reddit'
        """
        import praw
        print("Creating Reddit Object")
        try:
            reddit = praw.Reddit(
                client_id=self.reddit_config["client_id"],
                client_secret=self.reddit_config["client_secret"],
                user_agent=self.reddit_config["user_agent"],
                username=self.reddit_config["username"],
                password=self.reddit_config["password"]
            )
            print("Creation Complete")
            return reddit
        except Exception as error:
            print("Reddit Object Creation failed due to error:\n\t{error}".format(error=error))
            quit()

    def subreddit_list_scraper(self,reddit,subreddit,start_text=None,count=10,previous_posts=[]):
        """
        Uses the reddit object to take a number of the top records from a provided subreddit. Currently the number of
        posts this looks at is limited to 1000 so the maximum it can gather is 1000.

        :param reddit: Reddit object created by the praw library using the reddir config details passed to the RedditEmailer Class
        :type reddit: class 'praw.reddit.Reddit'
        :param subreddit: The name of the subreddit you wish to view. For example r/WritingPrompts can be provided as "WritingPrompts"
        :type subreddit: class 'str'
        :param start_text: Text that the posts you wish to examine start with. For example [WP] on writing prompts indicates the prompts themeselves
        :type start_text: class 'str'
        :param count: The number of posts you want to look for
        :type count: class 'int'
        :param previous_posts: A list of all the previous posts found by this code. By default it is set to an empty list.
        :type previous_posts: class 'list'

        :return submission_list: A list of all the collected submissions
        :rtype submission_list: class 'list'
        :return previous_posts: The previous posts object, updated to include the newly found posts
        :rtype previous_posts: class 'list'

        """

        print("Scraping posts from {sub}".format(sub=subreddit))
        try:
            subreddit = reddit.subreddit(subreddit)
            submission_list = []
            print("Subreddit: {sub} Found".format(sub=subreddit))

            for index,submission in enumerate(subreddit.top(limit=1000)):
                text = submission.title

                if text not in previous_posts:
                    if start_text:
                        if text.startswith(start_text):
                            previous_posts.append(text)
                            submission_list.append(submission)
                    else:
                        previous_posts.append(text)
                        submission_list.append(submission)

                if len(submission_list) >= count:
                    print("Found {count} posts".format(count=count))
                    break

            print("Subreddit scraping complete".format(count=count))
            return submission_list,previous_posts
        except Exception as error:
            print("Scraping failed due to error:\n\t{error}".format(error=error))
            quit()

    def previous_post_update(self,previous_posts,previous_posts_path,limit=100):
        """
        This function takes the newly updated previous_posts object and writes a number of the most recent unique posts
        to a text file at the provided fle path

        :param previous_posts: A list containing all the previous posts and the newly compiled posts
        :type previous_posts: class 'list'
        :param previous_posts_path: The path you want to save the previous posts to as a .txt file
        :type previous_posts_path: class 'str'
        :param limit: The number of most recent posts you wish to save to file
        :type limit: class 'int'

        """
        print("Updating the PreviousPosts file")
        try:
            # De-dupe the previous posts list
            previous_posts = list(set(previous_posts))
            # Check if there are over 100 previous posts, and if so take the most recent 100
            if len(previous_posts) > limit:
                previous_posts = previous_posts[-limit:]

            print("Writing previous posts to file")
            file = open(previous_posts_path, 'w', encoding='utf-8')
            file.write("\n".join(previous_posts))
            file.close()
            print("Update Complete")
        except Exception as error:
            print("Update Incomplete due to error:\n\t{error}".format(error=error))
            quit()

    def message_creation(self,submission_list,subject,removal_expressions=None):
        """
        This function creates the email message from the submissions scraped from Reddit

        :param submission_list: A list of the posts found from Reddit
        :type submission_list: class 'list'
        :param subject: The subject you wish to send the email with
        :type subject: class 'str'
        :param removal_expressions: a list containing any regular expressions you wish to remove from the posts
        :type removal_expressions: class 'list'
        :return email_message: The email message created using email.mime
        :rtype email_message: class 'email.mime.multipart.MIMEMultipart'

        """
        import re
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        print("Creating message from Submissions")

        try:
            email_message = MIMEMultipart("alternative")
            email_message["Subject"] = subject
            pattern_list = None

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

            print("Message successfully created from {number} submissions".format(number=len(submission_list)))
            return email_message
        except Exception as error:
            print("Message creation failed due to error:\n\t{error}".format(error=error))
            quit()

    def send_emails(self,message,fromEmail,fromPassword,distributionList):
        """
        A function for sending emails to a distribution list

        :param message: The email message created using email.mime
        :type message: class 'email.mime.multipart.MIMEMultipart'
        :param fromEmail: The email address of the account you want to send the emails from
        :type fromEmail: class 'str'
        :param fromPassword: The password for the account you want to send the emails from
        :type fromPassword: class 'str'
        :param distributionList: A list object containing a list of the email addresses you want to send the emails to
        :type distributionList: class 'list'

        """
        import smtplib

        print("Sending message to distribution list")
        try:
            print("Creating Gmail Session")
            session = smtplib.SMTP('smtp.gmail.com', 587)
            session.ehlo()
            session.starttls()
            session.ehlo()
            session.login(
                user=fromEmail,
                password=fromPassword
            )
            print("Session Created and Logged in")

            print("Sending emails")
            for toEmail in distributionList:
                session.sendmail(
                    msg=message.as_string(),
                    to_addrs=toEmail,
                    from_addr=fromEmail
                )
                print("Email sent to {toEmail}".format(toEmail=toEmail))
        except Exception as error:
            print("Email distribution failed due to error:\n\t{error}".format(error=error))
            quit()

def arguments():
    """
    Parses all the required arguments and returns them as the "args" object.
    Required Arguments include:

    1. subreddit - The subreddit to be analysed.
    2. config_path - The path to the json config file containing the Email and Reddit configs.
    3. previous_posts_path - The path to the txt file containing the previous posts. Defaults to None.
    4. subject - The subject to be applied to the email. Defaults to PythonGeneratedEmail.
    5. start_text - The start text of the reddit posts you wish to analyse. Defaults to None.
    6. count - The number of posts to be included in the email.

    :return args: Namespace object containing the parsed value for the argument assigned to it's corresponding name
    :rtype args: class 'argparse.Namespace'
    """


    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--subreddit")
    parser.add_argument("--config_path")
    parser.add_argument("--previous_posts_path",default=None)
    parser.add_argument("--subject",default="PythonGeneratedEmail")
    parser.add_argument("--start_text",default=None)
    parser.add_argument("--count", default=10,type=int)

    return parser.parse_args()

def main(config_path,subreddit,start_text,count,subject,previous_posts_path):
    """
    The main for RedditEmailer, such that if it's called from the command line it will perform the following steps:

    1. Load both configs from the config_path
    2. Create the Reddit Session
    3. Retrieve the posts from the provided subreddit
    4. Update the previous posts path to the previous_posts_path
    5. Create the email
    6. Send the email to the distribution list held in the email config

    :param config_path: The path to the json config file containing the Email and Reddit configs.
    :type config_path: class 'str'
    :param subreddit: The subreddit to be analysed.
    :type subreddit: class 'str'
    :param start_text: The start text of the reddit posts you wish to analyse.
    :type start_text: class 'str'
    :param count: The number of posts to be included in the email.
    :type count: class 'int'
    :param subject: The subject to be applied to the email.
    :type subject: class 'str'
    :param previous_posts_path: The path to the txt file containing the previous posts.
    :type previous_posts_path: class 'str'

    """

    import json
    import datetime

    file = open(config_path)
    config = json.load(file)
    file.close()

    session = RedditEmailer(
        reddit_config = config["connection_details"],
        email_config = config["email_config"],
        previous_posts_path = previous_posts_path
    )
    reddit = session.create_reddit_object()
    submission_list,previous_posts = session.subreddit_list_scraper(
        reddit=reddit,
        subreddit=subreddit,
        start_text = start_text,
        count=count,
        previous_posts=session.previous_posts
    )

    session.previous_post_update(
        previous_posts=previous_posts,
        previous_posts_path=session.previous_posts_path
    )

    message = session.message_creation(
        submission_list = submission_list,
        subject="{subject} - {date}".format(
            subject=subject,
            date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ),
        removal_expressions=config["email_config"]["removalExpressions"]
    )

    session.send_emails(
        message=message,
        fromEmail=session.email_config["fromEmail"],
        fromPassword=session.email_config["fromPassword"],
        distributionList=session.email_config["distributionList"]
    )

if __name__ == '__main__':
    args = arguments()
    main(
        subreddit=args.subreddit, # e.g. all for r/all
        config_path=args.config_path, # Path to the config
        subject=args.subject, # Subject you want for the Email
        start_text=args.start_text, # Start text for the posts to filter by (i.e [WP] is the start of titles on r/WritingPrompts
        count=args.count,# Number of responses you want to send
        previous_posts_path = args.previous_posts_path # Path to the text file containing a list of previous posts
    )

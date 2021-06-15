from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class email_handler():

    def __init__(self,fromEmail,fromPassword):

        self.session = self.create_session(
            fromEmail=fromEmail,
            fromPassword=fromPassword
        )

    def message_creation(self,subject,text_content):

        email_message = MIMEMultipart("alternative")
        email_message["Subject"] = subject
        email_message.attach(
            MIMEText(text_content)
        )

        return email_message

    def create_session(self,fromEmail,fromPassword):

        print("Creating Gmail Session")
        try:
            session = smtplib.SMTP('smtp.gmail.com', 587)
            session.ehlo()
            session.starttls()
            session.ehlo()
            session.login(
                user=fromEmail,
                password=fromPassword
            )
            print("Session Created and Logged in")
            return session
        except Exception as error:
            print("Session Creation failed due to error:\n\t{error}".format(error=error))
            quit()

    def send_emails(self,session, message, distributionList):

        print("Sending message to distribution list")
        try:
            print("Sending emails")
            for toEmail in distributionList:
                session.sendmail(
                    msg=message.as_string(),
                    to_addrs=toEmail,
                    from_addr=session.user
                )
                print("Email sent to {toEmail}".format(toEmail=toEmail))
        except Exception as error:
            print("Email distribution failed due to error:\n\t{error}".format(error=error))
            quit()
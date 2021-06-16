import sqlite3
from jinja2 import Template
import argparse
import pandas as pd
import gspread
from datetime import datetime
from dateutil import relativedelta
from threading import Timer

from Gmail import email_handler


def monthly_loop(function):
    today = datetime.today()

    next_month = today + relativedelta.relativedelta(months=1)
    next_month = next_month.replace(day=1, hour=8, minute=0, second=0, microsecond=0)
    delta_m = next_month - today

    secs = int(delta_m.total_seconds()) + 1
    print(secs)

    #
    # t = Timer(secs, run.send_monthly_questions)
    # t.start()

def daily_loop(function):
    today = datetime.today()

    next_day = today + relativedelta.relativedelta(days=1)
    next_day = next_day.replace(hour=8, minute=0, second=0, microsecond=0)

    delta_t = next_day - today

    secs = int(delta_t.total_seconds()) + 1
    print(secs)

    # t = Timer(secs, function)
    # t.start()

class Mementos():

    def sql_value_load(self,table, columns, values):

        with open("SQLFiles/value_load.sql", 'r') as file:
            query = Template(file.read())

        return query.render(
            table=table,
            columns=columns,
            values=values
        )

    def load_scrap(self):
        import csv

        def csv_file_load(file_path,table):

            with open(file_path, 'r') as file:
                results = csv.reader(file.readlines())
                columns = results.__next__()

            query = self.sql_value_load(
                table=table,
                columns=",\n".join(columns),
                values=",\n".join(
                    [f"({term})" for term in [",".join([f"'{value.strip()}'" for value in result]) for result in results]]
                )
            )

            self.database.execute(query)
            self.database.commit()

        scrap_dict = \
            {
                "EMAILS":"ScrapDataLoad/EMAILS.csv"
                , "QUESTIONS":"ScrapDataLoad/QUESTIONS.csv"
            }
        for table in scrap_dict:
            csv_file_load(
                table=table,
                file_path=scrap_dict[table]
            )

    def initialise_database(self,path):

        print("Attempting Database Initialisation")

        if path.split(".")[-1] != 'db':
            print("Incorrect File Extension provided. Please provide a path with a .db file")
            quit()
        else:
            self.database = sqlite3.connect(path)

            with open(r"SQLFiles/initial_ddl.sql",'r') as file:
                script = file.read()
                self.database.executescript(script)

        print("Initialisation Complete")

    def __init__(self, db_path,email_handler,gconn_path='GoogleCredentials.json'):
        self.initialise_database(db_path)
        self.email_handler = email_handler
        self.gconnection = gspread.service_account(filename=gconn_path)

    ## QUESTION HANDLING
    def load_questions_from_form(self):
        print(1)
        # Here I want to load new questions to the database from the Question Log sheet

    def low_question_alert(self):
        question_count = self.database.execute("SELECT COUNT(1) FROM QUESTIONS WHERE SENT = 0")
        #Here I want the tool to send me an email if the Reserve of unsent questions is getting low

    def load_random_question(self):

        valid_questions = pd.read_sql_query(
            sql='SELECT * FROM QUESTIONS WHERE SENT = 0',
            con=self.database
        )
        question = valid_questions.sample()

        return question.question_id.values[0],question.question_text.values[0]

    def update_sent_question(self,question_id):

        query = f"UPDATE QUESTIONS SET sent = 1 WHERE question_id = {question_id}"
        self.database.execute(query)

    # EMAIL HANDLING

    def load_mailing_list(self):

        mailing_list = pd.read_sql_query(
            sql='SELECT * FROM EMAILS',
            con=self.database
        )

        return mailing_list

    def send_monthly_questions(self,loop=True):

        month = datetime.utcnow().strftime('%B')
        run_datetime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]

        mailing_list = self.load_mailing_list()

        with open("EmailTemplate.txt", 'r') as template_file:
            message = Template(template_file.read())

        question_id, question_text = self.load_random_question()

        for index, row in mailing_list.iterrows():
            toEmail = row.email_address
            email_id = row.email_id

            email_text = message.render(
                user=row.owner_first_name,
                month=month,
                link=f"https://docs.google.com/forms/d/e/1FAIpQLScOg788QCxlmCV4zcjD3bcBu8yjRZQZqFXRCiwBS2hzhjftfg/viewform?usp=pp_url&entry.1110074174={toEmail}&entry.1028672538={question_id}",
                question_id=question_id,
                question=question_text
            )

            subject = f"{month}'s Mementos Question"

            email_message = self.email_handler.message_creation(
                subject=subject,
                text_content=email_text
            )
            self.email_handler.send_email(
                message=email_message,
                toEmail=toEmail
            )

            self.add_sent_record(
                email_id=email_id
                ,question_id=question_id
                ,datetime_sent=run_datetime
            )

        if loop:
            monthly_loop(self.send_monthly_questions)

    # CORRESPONDENCE HANDLING

    def add_sent_record(self,email_id,question_id,datetime_sent):
         sql = f"INSERT INTO CORRESPONDENCE(email_id,question_id,datetime_sent) " \
               f"VALUES({email_id},{question_id},'{datetime_sent}')"
         self.database.execute(sql)
         self.database.commit()

    def get_responses(self, gconnection=None):

        if gconnection is None:
            gconnection = self.gconnection

        workbook = gconnection.open("BYT Mementos (Responses)")
        sheet = workbook.worksheet('Form Responses')

        max_timestamp = self.database.execute("SELECT MAX(datetime_received) FROM CORRESPONDENCE").fetchone()[0]

        data = sheet.get_all_values()
        headers = data.pop(0)
        results = pd.DataFrame(data, columns=headers)

        if max_timestamp:
            results = results[results['Timestamp'] >= max_timestamp]

        return results

    def get_email_id(self,email_address):

        sql = f"SELECT MAX(email_id) FROM EMAILS WHERE email_address = '{email_address}'"
        email_id = self.database.execute(sql)
        return email_id.fetchone()[0]

    def response_update(self,loop=True):

        for index,response in self.get_responses().iterrows():
            email_id = self.get_email_id(response.get("Email"))
            question_id = response.get("Question Number")

            received_timestamp = response.get("Timestamp")
            answer = response.get("Answer")
            sql = f"UPDATE CORRESPONDENCE SET datetime_received = '{received_timestamp}', response_text = '{answer}'" \
                  f" WHERE email_id={email_id} AND question_id={question_id};"
            self.database.execute(sql)
            self.database.commit()

        if loop:
            daily_loop(self.response_update)

def arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument("--db_path")
    parser.add_argument("--fromEmail")
    parser.add_argument("--fromPassword")
    parser.add_argument("--setting",default="auto",choices=["auto","quiz","response"])

    return parser.parse_args()

if __name__ == '__main__':
    args = arguments()
    emails = email_handler(
        fromEmail=args.fromEmail,
        fromPassword=args.fromPassword
    )
    run = Mementos(
        db_path=args.db_path,
        email_handler = emails
    )

    if args.setting == "auto":
        daily_loop(run.response_update)
        monthly_loop(run.send_monthly_questions)
    elif args.setting == "quiz":
        run.send_monthly_questions(loop=False)
    elif args.setting == "response":
        run.response_update(loop=False)

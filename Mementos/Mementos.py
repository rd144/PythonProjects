import sqlite3
from jinja2 import Template
import argparse

from Gmail import email_handler

class Mementos():

    def load_scrap(self):
        import csv

        def sql_value_load(table, columns, values):

            with open("SQLFiles/value_load.sql", 'r') as file:
                query = Template(file.read())

            return query.render(
                table=table,
                columns=columns,
                values=values
            )

        def csv_file_load(file_path,table):

            with open(file_path, 'r') as file:
                results = csv.reader(file.readlines())
                columns = results.__next__()

            query = sql_value_load(
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
                , "RESPONSE": "ScrapDataLoad/RESPONSE.csv"
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

    def __init__(self, db_path):
        self.initialise_database(db_path)

##TODO - Comment out Load Scrap in final run
##TODO - Add Logger
def arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument("--db_path")
    parser.add_argument("--fromEmail")
    parser.add_argument("--fromPassword")

    return parser.parse_args()

if __name__ == '__main__':
    args = arguments()

    emails = email_handler(
        fromEmail=args.fromEmail,
        fromPassword=args.fromPassword
    )
    run = Mementos(
        db_path=args.db_path
    )
    run.load_scrap()

"""
Created by Ross Dingwall on the 25th of November 2020.

Recipe Manager is a python based class that will allow a user to add, remove, and modify recipes stored within a
JSON file.

It is designed to be used in conjunction with a Kivy front end and another funtion "Meal Planner" to allow a user to
plan their meals for the week at a push of a button.

Future scope increase include:
    Recipe Scraping (both from Web and photographs)
    Macro Lookup from Ingredient Name
    Standardize Measurements
    Standardize Ingredients using the Food Database API (https://world.openfoodfacts.org/data)
"""

import json
import os



class RecipeManager():

    def __init__(self):

        # Check if recipe JSON Exists
        self.recipe_path = os.sep.join(["docs","recipe_log.json"])
        if os.path.isfile(self.recipe_path):
            print("Exists")
            with open(self.recipe_path,'r') as f:
                self.recipes = json.load(f)
        else:
            print("Doesnt Exist")
            self.recipes = {}

if __name__ == '__main__':
    RecipeManager()
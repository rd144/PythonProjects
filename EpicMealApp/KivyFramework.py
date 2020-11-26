"""
Created by Ross Dingwall on the 25th of November 2020.

This file is to be the Kivy Framework that holds together the two functions, "Meal Planner" and "Recipe Manager"

The UI must be:
    1. Intuitive
    2. Pleasing
    3. Simple
    4. Descriptive (Provides Feedback)

Current Scope: 4 pages (Title Page, Recipe Log, Add Recipe, Meal Plan)
For now it can work just on the one computer, but ideally I'd like people to be able to share recipes etc and
build a backlog (if this gets crazy, may need to look into compression or alternative storage methods aside from JSON)


"""

import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown

from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen

import os

kivy.require('2.0.0')


#TODO - Take a look into KivyMD for better designed widgets

class RecipeManager(GridLayout):

    def __init__(self,**kwargs):
        # Basically tells GridLayout to initialise
        super().__init__(**kwargs)
        self.cols = 1

        self.title = TextInput(text="<Name of Dish>", multiline=False)
        self.add_widget(self.title)

        self.source = TextInput(text="<Source for Recipe>", multiline=False)
        self.add_widget(self.source)


        details_layout = GridLayout()
        details_layout.cols = 2

        # TODO - Add search function for existing ingredients used in other recipes to try and maintain order
        self.ingredient_label = Label(text="Ingredient :")
        details_layout.add_widget(self.ingredient_label)
        self.ingredient_item = TextInput(text="<Name of Ingredient>", multiline=False)
        details_layout.add_widget(self.ingredient_item)

        # TODO - Add Validations on the inputs given here to ensure only Numeric Inputs are provided
        self.quantity_label = Label(text="Quantity :")
        details_layout.add_widget(self.quantity_label)
        self.quantity_item = TextInput(text="<Amount of Ingredient>", multiline=False)
        details_layout.add_widget(self.quantity_item)

        # TODO - Implement this as a drop down
        # Drop down with list of standard Units (For use with Unit conversion later)
        self.unit_label = Label(text="Unit :")
        details_layout.add_widget(self.unit_label)
        self.unit_item = TextInput(text="<Unit Used>", multiline=False)
        details_layout.add_widget(self.unit_item)

        self.add_widget(details_layout)

class EpicMealTime(App):

    def build(self):

        self.screen_manager = ScreenManager()
        self.recipe_manager = RecipeManager()

        screen = Screen(name="RecipeManager")
        screen.add_widget(self.recipe_manager)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

if __name__ == '__main__':
    application = EpicMealTime()
    application.run()



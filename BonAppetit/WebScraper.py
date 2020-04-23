from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import time
import datetime
import json

def create_chrome_session(url):

    # create a new Chrome session
    driver = webdriver.Chrome()
    driver.implicitly_wait(30)
    driver.get(url)
    return driver

def recipe_detail_extraction(driver,recipe_link):

    def value_text_return(value):
        if value:
            return value.text

    recipe_details = {}
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(recipe_link)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    recipe_details["contributor"] = value_text_return(soup.find("span",class_="contributor-name"))
    details = value_text_return(soup.find("script",type="application/ld+json"))
    details = "".join([char for char in details if char.isascii()])

    try:
        details = json.loads(details)
        recipe_details["ingredients"] = details["recipeIngredient"]
        recipe_details["name"] = details["name"]
        recipe_details["dateCreated"] = details["dateCreated"]
        recipe_details["datePublished"] = details["datePublished"]
        recipe_details["image_link"] = details["image"]
        instructions = {}
        for index, detail in enumerate(details["recipeInstructions"]):
            instructions[index + 1] = detail["text"]

        recipe_details["instructions"] = instructions

    except Exception as e:
        print("Error : {0} found for page {1}".format(e,recipe_link))
        print(e)

        recipe_details["ingredients"] = None
        recipe_details["name"] = None
        recipe_details["dateCreated"] = None
        recipe_details["datePublished"] = None
        recipe_details["image_link"] = None
        recipe_details["instructions"] = None


    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return recipe_details

def find_recipes(driver,scraped_recipes={}):

    soup = BeautifulSoup(driver.page_source, 'lxml')
    recipes = soup.find_all('a',href=re.compile("recipe"),text='SEE RECIPE')

    for recipe_element in recipes:
        recipe_link = "".join(["https://www.bonappetit.com/",recipe_element.attrs["href"]])
        if recipe_link not in scraped_recipes:
            recipe_details = recipe_detail_extraction(driver,recipe_link)
            scraped_recipes[recipe_link] = recipe_details

    return scraped_recipes

def open_new_page(driver,page):

    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.TAB)

    windows = driver.window_handles

    time.sleep(3)
    driver.switch_to.window(windows[1])

def extract_more_recipes(more_button):

    more_button.send_keys(Keys.RETURN)
    more_button.send_keys(Keys.RETURN)

    time.sleep(1)

def main():

    start = datetime.datetime.utcnow()
    scraped_recipes = {}
    driver = create_chrome_session("https://www.bonappetit.com/recipes")
    more_button = driver.find_element_by_xpath('//*[@id="react-app"]/div/div/div[2]/div[1]/div/div/button')

    while len(scraped_recipes) < 100:
        scraped_recipes = find_recipes(driver)
        more_button.send_keys(Keys.RETURN)
        more_button.send_keys(Keys.RETURN)
        more_button.send_keys(Keys.RETURN)
        print("Found {0} Recipes".format(len(scraped_recipes)))
        time.sleep(1)

    for recipe in scraped_recipes:
        print(recipe)

    time_taken = (datetime.datetime.utcnow() - start).total_seconds()
    print("Scraped {0} recipes from Bon Appetit in {1} seconds".format(len(scraped_recipes),time_taken))

if __name__ == '__main__':
    main()







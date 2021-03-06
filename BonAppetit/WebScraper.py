from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import time
import datetime
import json
import glob
import os

def create_chrome_session(url):

    # create a new Chrome session
    driver = webdriver.Chrome(ChromeDriverManager().install())
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

def find_recipes(driver,scraped_recipes,recipe_count):

    soup = BeautifulSoup(driver.page_source, 'lxml')
    recipes = soup.find_all('a',href=re.compile("recipe"),text='SEE RECIPE')

    for recipe_element in recipes:
        recipe_link = "".join(["https://www.bonappetit.com/",recipe_element.attrs["href"]])
        if recipe_link not in scraped_recipes:
            recipe_count += 1
            recipe_details = recipe_detail_extraction(driver,recipe_link)
            scraped_recipes[recipe_link] = recipe_details

    return scraped_recipes,recipe_count

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

def gather_recipe_loop(driver,more_button,limit=500):

    recipe_count = 0
    scraped_recipes = {}
    same_count = 0
    output_file_path = 'C:\\Users\\Ross\\Desktop\\GIT\\PythonProjects\\BonAppetit\\Recipes\\Recipes{0}.json'
    try:
        while same_count <= 5:
            length = len(scraped_recipes)
            scraped_recipes,recipe_count = find_recipes(driver,scraped_recipes,recipe_count)

            if length == len(scraped_recipes):
                same_count += 1
            elif length <= len(scraped_recipes) and same_count > 0:
                same_count = 0

            if len(scraped_recipes) >= limit:
                file = open(output_file_path.format(datetime.datetime.utcnow().strftime('%y%m%dT%H%M%S')), 'w')
                json.dump(scraped_recipes, file, indent=2)
                file.close()
                scraped_recipes = {}

            more_button.send_keys(Keys.RETURN)
            print("Found {0} Recipes".format(recipe_count))
        return recipe_count
    except KeyboardInterrupt:
        print("Manually stopped by user. Writing current results from memory to file")
        file = open(output_file_path.format(datetime.datetime.utcnow().strftime('%y%m%dT%H%M%S')), 'w')
        json.dump(scraped_recipes, file, indent=2)
        file.close()
        return recipe_count
    except Exception as e:
        print("Unknown error pervented the code from running: {0}".format(e))
        print("Writing current results from memory to file")
        file = open(output_file_path.format(datetime.datetime.utcnow().strftime('%y%m%dT%H%M%S')), 'w')
        json.dump(scraped_recipes, file, indent=2)
        file.close()
        return recipe_count

def combine_recipes(recipe_directory):

    combined_dict = {}
    for file_path in glob.iglob(recipe_directory + '/**/*', recursive=True):
        if os.path.isfile(file_path) and file_path.endswith('.json'):
            try:
                file = open(file_path, 'r')
                recipe_dict = json.load(file)
                file.close()
                for key in recipe_dict:
                    if key not in combined_dict:
                        combined_dict[key] = recipe_dict[key]
            except json.JSONDecodeError:
                print("Unable to process file: {file} as JSON".format(file=os.path.basename(file_path)))

    print("Combined : {0}".format(len(combined_dict)))
    return combined_dict

def recipes_to_df(recipes, output_path):
    def key_check_and_return(dict, key):
        if key in dict:
            return dict[key]
        else:
            return None

    df = pandas.DataFrame()

    for index, link in enumerate(recipes):

        link_dict = recipes[link]

        if index % 100 == 0 and index != 0:
            print('Processed {index}/{length} links'.format(index=index, length=len(recipes)))

        contributor = key_check_and_return(link_dict, 'contributor')
        ingredients = key_check_and_return(link_dict, 'ingredients')
        if type(ingredients) is list:
            number_of_ingredients = len(ingredients)
            ingredients = ",".join(ingredients)
        else:
            number_of_ingredients = None

        name = key_check_and_return(link_dict, 'name')
        try:
            date_created = key_check_and_return(link_dict, 'dateCreated')
            date_created = datetime.datetime.strptime(date_created[:19], "%Y-%m-%dT%H:%M:%S")
        except:
            date_created = None

        try:
            date_published = key_check_and_return(link_dict, 'datePublished')
            date_published = datetime.datetime.strptime(date_published[:19], "%Y-%m-%dT%H:%M:%S")
        except:
            date_published = None

        image_link = key_check_and_return(link_dict, 'image_link')
        instructions = key_check_and_return(link_dict, 'instructions')
        if type(instructions) is dict:
            number_of_steps = len(instructions)
            instruction_order = sorted(instructions)
            instruction_text = ""
            for step in instruction_order:
                instruction_text = instruction_text + "{step} : {instruction}\n".format(step=step,
                                                                                        instruction=instructions[step])
        else:
            instruction_text = None
            number_of_steps = None

        df = df.append({
            'URL': link,
            'Contributor': contributor,
            'Ingredients': ingredients,
            'Number of Ingredients': number_of_ingredients,
            'Dish Name': name,
            'Date Created': date_created,
            'Date Published': date_published,
            'Instructions': instruction_text,
            'Number of Steps': number_of_steps,
            'Image Link': image_link
        }, ignore_index=True)

    contributor_df = df.groupby('Contributor').agg({
        'Number of Steps': 'mean',
        'Number of Ingredients': 'mean',
        'URL': 'count',
        'Date Published': ['max', 'min'],
        'Date Created': ['max', 'min']
    })

    output = pandas.ExcelWriter(output_path)

    df.to_excel(output, sheet_name='Ungrouped')
    contributor_df.to_excel(output, sheet_name='Grouped')

    print('Written to {0}'.format(output.path))
    output.close()

def main():

    start = datetime.datetime.utcnow()

    driver = create_chrome_session("https://www.bonappetit.com/recipes")
    more_button = driver.find_element_by_xpath('//*[@id="react-app"]/div/div/div[2]/div[1]/div/div/button')
    recipe_count = gather_recipe_loop(driver, more_button)
    time_taken = (datetime.datetime.utcnow() - start).total_seconds()
    print("Scraped {0} recipes from Bon Appetit in {1} seconds".format(recipe_count,time_taken))

if __name__ == '__main__':
    main()







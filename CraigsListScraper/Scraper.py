"""
Created by Ross Dingwall. Scraper.py is a script to look at all property listings on Craigslist and return those within
provided parameters (including: neighbourhoods, GeoFence coordinates, budget,min/max bedrooms etc.)
"""

from craigslist import CraigslistHousing
import datetime
import pandas
import argparse
import json

def config_parser(config_path):
    """
    A function for loading the config from the provided JSON file and returning the parts required

    :param config_path: The path to the config provided by the arguments
    :type config_path: class 'str'
    :return filters: A Dictionary object containing the filters desired for pulling from CraigslistHousing
    :rtype filters: class 'dict'
    :return boxes: A Dictionary object containing any GeoFence boxes you wish to check if the property is within
    :rtype boxes: class 'dict'
    :return neighbourhoods: A List object of all the neighbourhoods you wish to check if the property is within
    :rtype neighbourhoods: class 'list'

    """

    print("Parsing the config from : {path}".format(path=config_path))
    try:
        file = open(config_path,'r')
        config = json.load(file)
        file.close()
    except Exception as e:
        print("Error Encounted parsing config : {error}".format(error=e))
        print("Config defaulted to empty dict for remainder of the code")
        config = {}

    print("JSON Config loaded correctly")

    config = {key.lower(): value for key, value in config.items()}

    if "filters" in config:
        print("Filters found in keys")
        filters = config["filters"]
    else:
        print("Filters not found in keys")
        filters = {}

    if "boxes" in config:
        print("Boxes found in keys")
        boxes = config["boxes"]
    else:
        print("Boxes not found in keys")
        boxes = {}

    if "neighbourhoods" in config:
        print("Neighbourhoods found in keys")
        neighbourhoods = config["neighbourhoods"]
        neighbourhoods = [hood.lower() for hood in neighbourhoods]
    else:
        print("Neighbourhoods not found in keys")
        neighbourhoods = []

    return filters,boxes,neighbourhoods

def location_check(result,boxes,neighbourhoods):
    """
    A function for checking if a result is in the correct location. If the result contains GeoTag information it will
    check if it's within the boxes provided. If no GeoTag information is present, it will check the neighbourhoods.

    :param result: Dictionary Object returned from CraigslistHousing that contains the results for each listing
    :type result: class 'dict'
    :param boxes: Dictionary Object containing the coordinates of GeoFences required
    :type boxes: class 'dict'
    :param neighbourhoods: List object containing the desired neighbourhoods
    :type neighbourhoods: class 'list'
    :return True/False: A Boolean object that is set to True if the Result is present in either the Boxes or the Neighbourhoods
    :rtype True/False: class 'bool'

    """

    def in_box(coords, box):
        """
        A sub-function that checks if the given coordinates are present in the GeoFence box. Returns true or false
        depending on whether the coordinates are in or out of the box.

        :param coords: The coordinates you want to check. In the form [x,y]
        :type coords: class 'list'
        :param box: The box you want to check if the coordinates are within in the form [[x1,y1],[x2,y2]]
        :type box: class 'list'

        """

        x_list = sorted([box[0][1], box[1][1]])
        y_list = sorted([box[0][0], box[1][0]])
        try:
            if x_list[0] <= coords[0] <= x_list[1] and y_list[0] <= coords[1] <= y_list[1]:
                return True
            return False
        except Exception as e:
            print("Error Encountered : {error}".format(error=e))
            quit()

    if result["geotag"]:
        for name, coords in boxes.items():
            if in_box(result["geotag"], coords):
                return True
    else:
        if result["where"]:
            if result["where"].lower() in neighbourhoods:
                return True
    return False

def output_to_excel(output_df,output_path,column_order):
    """
    A function that first checks if any results have been found. If they have, it re-orders them and writes the report
    to Excel a the path provided.

    :param output_df: The DataFrame object containing the results you wish to be output
    :type output_df: class 'pandas.core.frame.DataFrame'
    :param column_order: A list of columns in the order you want the dataframe to be presented
    :type column_order: class 'list'
    :param output_path: The path you wish the Excel file to be written to
    :type output_path: class 'str'

    """

    if output_df.any:
        output_df = output_df[column_order].sort_values(["Price", "Location", "Last Updated"],ascending=True).drop_duplicates()
        print("Writing to Excel")
        output_df.to_excel(output_path, index=False)
    else:
        print("No Results Found")

def main(config_path,site,category):
    """
    The main portion of the code, main calls the other functions in order and does any additional analysis required.

    :param config_path: File path for the JSON config file.
    :type config_path: class 'str'
    :param site: The site you wish to analyse
    :type site: class 'str'
    :param category: The sub-category desired, taken from CraigsList (For example, https://vancouver.craigslist.org/pml/ the sub-category is "pml")
    :type category: class 'str'
    :return output_df: A df containing the anaylsed results.
    :rtype output_df: class 'pandas.core.frame.DataFrame'

    """

    count = 0
    output_df = pandas.DataFrame()
    filters,boxes,neighbourhoods = config_parser(config_path)

    results = CraigslistHousing(
        site=site,
        category=category,
        filters=filters
    ).get_results(sort_by='newest')

    for index,result in enumerate(results):

        if location_check(result,boxes,neighbourhoods):
            output_df = output_df.append({
                "Full Result" : str(result),
                "Price" : str(result["price"]),
                "Description" : str(result["name"]),
                "URL": "=HYPERLINK(\"{0}\")".format(str(result["url"])),
                "Location": str(result["where"]).title(),
                "Last Updated": str(result["last_updated"])
            },ignore_index=True)

            count = count + 1

        if index % 100 == 0 and index != 0:
            print("Analysed {0} Results, {1} Found matching location criteria".format(index,count))

    print("Analysis Complete. Found {0} properties matching the criteria".format(count))

    return output_df

def arguments():
    """
    Parses all the required arguments and returns them as the "args" object.
    Required Arguments include:

    1. config_path - The path to the json config file.
    2. site - The location you want to investigate.
    3. output_path - The path to the .xlsx file you want to write the results to.
    4. category - The craigslist category you wish to investigate.

    :return args: Namespace object containing the parsed value for the argument assigned to it's corresponding name
    :rtype args: class 'argparse.Namespace'
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--config_path")
    parser.add_argument("--site")
    parser.add_argument("--output_path")
    parser.add_argument("--category",default=None)

    args = parser.parse_args()

    return args

if __name__ == '__main__':

    start = datetime.datetime.utcnow()
    print("Code Initiated")

    args = arguments()
    output_df = main(
        config_path=args.config_path,
        site=args.site,
        category=args.category
    )

    column_order = [
        "Description",
        "Location",
        "Price",
        "Last Updated",
        "URL",
        "Full Result"
    ]

    output_to_excel(output_df,args.output_path,column_order)

    print("Code Completed in {0} Seconds".format((datetime.datetime.utcnow()-start).total_seconds()))

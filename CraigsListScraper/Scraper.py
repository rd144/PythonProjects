from craigslist import CraigslistHousing
import datetime
import pandas

def in_box(coords, box):

    x_list = sorted([box[0][1],box[1][1]])
    y_list = sorted([box[0][0],box[1][0]])
    try:
        if x_list[0]<= coords[0] <= x_list[1] and y_list[0]<= coords[1] <= y_list[1]:
            return True
        return False
    except:
        print(x_list)
        print(y_list)
        print(coords)
        quit()

def location_check(result):

    boxes = {
        'general' : [[-123.150817,49.231317],[-123.026187,49.295643]]
    }

    neighbourhoods = ["brentwood","burnaby","skytrain","mt pleasant","kitsilano","metrotown","renfrew-collingwood","yaletown","coal harbour","gastown"]

    if result["geotag"]:
        for name, coords in boxes.items():
            if in_box(result["geotag"], coords):
                return True
    else:

        if result["where"]:
            if result["where"].lower() in neighbourhoods:
                return True
            else:
                return False

def main():

    count = 0
    cl_h = CraigslistHousing(
        site='vancouver',
        category='apa',
        filters={
            'max_price': 2700,
            'min_price': 1800,
            'bundle_duplicates': True,
            'has_image': True,
            'min_bedrooms': 2,
            'max_bedrooms': 2
        }
    )

    output_df = pandas.DataFrame()

    results = cl_h.get_results(
        sort_by='newest')

    for index,result in enumerate(results):

        if location_check(result):

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

    # Clean up the DataFrame
    output_df = output_df[
        [
            "Description",
            "Location",
            "Price",
            "Last Updated",
            "URL",
            "Full Result",
        ]
    ].sort_values(["Price","Location","Last Updated"],ascending=True).drop_duplicates()

    print("Writing to Excel")
    directory = 'C:\\Users\\Ross\\PycharmProjects\\CraigsListScraper\\'
    output_df.to_excel(directory+"PropertyReport{0}.xlsx".format(datetime.date.today()),index=False)

if __name__ == '__main__':
    start = datetime.datetime.utcnow()
    print("Code Initiated")
    main()
    print("Code Completed in {0} Seconds".format((datetime.datetime.utcnow()-start).total_seconds()))
import glob
import os

from ebooklib import epub
import re
import json

source_directory = "C:\\Users\\Ross\\Google Drive\\Calibre Library\\"
output_path = "/Config.json"
book_list = []
non_num_patt = re.compile("[^\d]")
output_dict = {}

for file_path in glob.glob(source_directory+"/**/*",recursive=True):
    if ".epub" in file_path:
        if os.path.basename(file_path) not in book_list:
            print("Processing {file}".format(file=os.path.basename(file_path)))
            book_list.append(os.path.basename(file_path))
            author = file_path.replace(source_directory,"").split("\\")[0]
            book = epub.read_epub(file_path)
            term_count = {}
            for item in book.get_items_of_media_type("application/xhtml+xml"):
                print(item)
                name = str(item).split(":")[1]
                non_numerical = "".join(non_num_patt.findall(name))
                if non_numerical in term_count:
                    term_count[non_numerical] += 1
                else:
                    term_count[non_numerical] = 1
            term = max(term_count, key=term_count.get)

            output_dict[file_path] = {
                "author" : author,
                "tag_expression" : "",
                "chapter_flag" : term
            }

output_file = open(output_path,'w')
json.dump(output_dict,output_file,indent=4,sort_keys=True)



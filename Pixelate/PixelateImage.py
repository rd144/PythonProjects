"""
A Python script for pixelating an image from a file path at different levels of granularity.

Created by Ross Dingwall - 2020-12-07
"""

from PIL import Image

def pixelate(input_path,output_path=None,pixelate_dim=16):

    # Open Image
    img = Image.open(input_path)

    # Resize smoothly down to square pixels defined by arguments
    imgSmall = img.resize((pixelate_dim, pixelate_dim), resample=Image.BILINEAR)

    # Scale back up using NEAREST to original size
    result = imgSmall.resize(img.size, Image.NEAREST)

    if output_path:
        # Save
        result.save(output_path)
    else:
        result.show()

def poster_iteration(poster_folder,move_original=False,starting_pixels=4,starting_step=2,step_increment=3,max_steps=5):
    import os
    import glob


    files = glob.glob(poster_folder+"**\*")
    files = list(filter(os.path.isfile,files))

    for path in files:

        base_name = os.path.basename(path)
        print(f"Pixelating {base_name}")

        dir_name = os.sep.join([os.path.dirname(path), "".join(base_name.split(".")[0:-1])])

        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)

        pixels = starting_pixels
        step = starting_step

        step_count = 1
        while step_count <= max_steps:

            output_path = "{folder}{seperator}Pixelated_{pixel_count}_{basename}".format(
                folder=dir_name
                , seperator=os.sep
                , pixel_count=pixels
                , basename=base_name
            )

            pixelate(
                input_path=path
                , output_path = output_path
                , pixelate_dim=pixels
            )

            print(f"Pixelated at {pixels}x{pixels}")

            step += step_increment
            pixels += step
            step_count += 1

        if move_original:
            os.rename(path,os.sep.join([dir_name, base_name]))

        print("Complete")

if __name__ == '__main__':
    poster_folder = r"C:\Users\Ross\Desktop\Posters"
    poster_iteration(poster_folder)

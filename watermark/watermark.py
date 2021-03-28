#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jun 16 2020
@author: MohammadHossein Salari
@sorces:
    - https://automatetheboringstuff.com/chapter17/
    - https://www.pyimagesearch.com/2016/04/25/watermarking-images-with-opencv-and-python/
    - https://pybit.es/pillow-intro.html
    - https://stackoverflow.com/questions/50963537/pil-make-image-transparent-on-a-percent-scale
"""
import argparse
import sys
import os
from PIL import Image


def watermark_image(watermark_path, input_image_path, scale_ratio, transparency, position, padding):
    padding = int(padding)
    # load watermark image
    try:
        watermark = Image.open(watermark_path)
    except IOError as e:
        sys.exit(f"Invalid Watermark image {e}")

    # load input image
    try:
        input_image = Image.open(input_image_path)
    except IOError as e:
        sys.exit(f"Invalid Input image {e}")

    # resize watermark so it fits the input image
    watermark_width, watermark_height = watermark.size
    input_image_width, input_image_height = input_image.size
    aspect_ratio = watermark_width / watermark_height
    new_watermark_width = input_image_width * scale_ratio
    new_watermark_height = input_image_height * scale_ratio
    watermark.thumbnail((new_watermark_width / aspect_ratio,
                         new_watermark_height / aspect_ratio), Image.ANTIALIAS)

    # make transparent mask from watermark
    if watermark.mode != 'RGBA':
        alpha = Image.new('L', watermark.size, 255)
        watermark.putalpha(alpha)

    paste_mask = watermark.split()[-1].point(
        lambda i: i * transparency)

    temp_image = input_image.copy()

    # add watermark to image
    if position in ["top_left", "topleft", "tl"]:
        temp_image.paste(watermark, (padding, padding), mask=paste_mask)
    elif position in ["bottom_left", "bottomleft", "bl"]:
        temp_image.paste(
            watermark, (padding, (temp_image.height - watermark.height-padding)), mask=paste_mask)

    elif position in ["top_right", "topright", "tr"]:
        temp_image.paste(
            watermark, ((temp_image.width - watermark.width-padding), padding), mask=paste_mask)

    elif position in ["bottom_right", "bottomright", "br"]:
        temp_image.paste(watermark, ((temp_image.width - watermark.width-padding),
                                     (temp_image.height - watermark.height-padding)), mask=paste_mask)

    elif position in ["center", "c"]:
        temp_image.paste(watermark, ((temp_image.width - watermark.width) //
                                     2, (temp_image.height - watermark.height)//2), mask=paste_mask)

    elif position == "tile":

        xpadding = (temp_image.width -
                    watermark.width*(temp_image.width // watermark.width))//2

        ypadding = (temp_image.height -
                    watermark.height*(temp_image.height // watermark.height))//2

        for raw, xpos in enumerate(range(0, temp_image.width, watermark.height)):

            # if raw >= temp_image.width // watermark.width:
            #     break
            for column, ypos in enumerate(range(0, temp_image.height, watermark.height)):
                # if column >= temp_image.height // watermark.height:
                #     break
                temp_image.paste(
                    watermark, (xpos - xpadding, ypos - ypadding),  mask=paste_mask)

    else:
        sys.exit(f"Invalid watermark position: {position}")

    return temp_image


if __name__ == "__main__":

    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-w", "--watermark", required=True,
                    help="path to watermark image (assumed to be transparent PNG)")
    ap.add_argument("-i", "--input", required=True,
                    help="path to the input image")
    ap.add_argument("-s", "--scale", type=float, default=0.25,
                    help="scale watermark in percent")
    ap.add_argument("-t", "--transparency", type=float, default=0.50,
                    help="transparency percent of the watermark  from 0 to 1 (smaller is more transparent)")

    ap.add_argument("-p", "--position", type=str, default="br",
                    help="watermark position: top bottom center| left right center (tl== top left)")
    args = vars(ap.parse_args())

    ap.add_argument("-padding", "--padding", type=int, default=10,
                    help="watermark padding in pixel")
    args = vars(ap.parse_args())

    watermark_path = os.path.realpath(args["watermark"])
    input_path = os.path.realpath(args["input"])
    scale_ratio = args["scale"]
    transparency = args["transparency"]
    position = args["position"]
    padding = args["padding"]

    output_image = watermark_image(
        watermark_path, input_path, scale_ratio, transparency, position, padding)

    output_image.show()

    output_image_path = os.path.join(os.path.dirname(os.path.realpath(input_path)),
                                     f'{os.path.splitext(input_path)[0]}_{position}.png')
    output_image.save(output_image_path, quality=100)

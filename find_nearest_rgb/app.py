import re
from typing import Union

import webcolors
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

from colors import XTERM_256_COLORS


def find_nearest_color(input_color: Union[tuple, str]) -> dict:

    try:
        input_color = webcolors.hex_to_rgb(input_color)
    except (TypeError, ValueError):
        input_color = tuple(input_color.split(", ")) if ", " in input_color else tuple(input_color.split(","))

    solved_results = [
        {
            "xterm_number": color["xterm_number"],
            "xterm_name": color["xterm_name"],
            "hex": color["hex"],
            "rgb": color["rgb"],
            "diff": delta_e_cie2000(
                convert_color(sRGBColor(*input_color), LabColor),
                convert_color(sRGBColor(*color["rgb"]), LabColor),
            )
        } for color in XTERM_256_COLORS
    ]

    return min(solved_results, key=lambda x: x["diff"])


def find_all_colors_in_file_and_write_result(xterm=False):

    with open("source.txt", "r") as file:
        lines = file.readlines()

    colors = list()
    for line in lines:
        color = re.findall(pattern=r"(\#.{6})|(\d{1,3},( |).+)", string=line.strip())
        try:
            color = color[0][0] or color[0][1]
        except IndexError:
            break
        if "====" in color:
            break
        colors.append(color)

    with open("source.txt", "a") as file:
        max_left_justify = max([len(c) for c in colors])
        data = [
            f"{c.ljust(max_left_justify)} ---> " \
            f"{find_nearest_color(c)['xterm_number'] if xterm else find_nearest_color(c)}\n"
            for c in colors
        ]
        file.write('\n\n' + " RESULT ".center(max([len(d) for d in data]), "#") + '\n')
        for d in data:
            file.write(d)
        file.write("".center(max([len(d) for d in data]), "#"))
        file.write("\n")


if __name__ == '__main__':
    find_all_colors_in_file_and_write_result()

import os
import json
import cv2
import numpy as np
import math
from uncertainties import ufloat


def get_distance(point1, point2):
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)


def get_rotation(outline):
    # Get the minimum area rectangle
    rect = cv2.minAreaRect(outline)

    # Get the rotation angle
    angle = rect[-1]

    # From https://www.pyimagesearch.com/2017/02/20/text-skew-correction-opencv-python/
    # The `cv2.minAreaRect` function returns values in the range [-90, 0);
    # As the rectangle rotates clockwise the returned angle trends to 0 --
    # In this special case we need to add 90 degrees to the angle
    if angle < -45:
        angle = -(90 + angle)
    # Otherwise, just take the inverse of the angle to make it positive
    else:
        angle = -angle

    final_angle = angle + 90

    if final_angle < 5:
        final_angle = 0

    return final_angle


def get_coords(box):
    x = math.inf
    y = math.inf

    for coords in box:
        if coords[0] < x:
            x = coords[0]
        if coords[1] < y:
            y = coords[1]

    return (x, y)


def get_size(box):
    if get_distance(box[0], box[1]) > get_distance(box[1], box[2]):
        width = get_distance(box[1], box[2])
        length = get_distance(box[0], box[1])
    else:
        width = get_distance(box[0], box[1])
        length = get_distance(box[1], box[2])

    return (width, length)


# Ne peut pas marcher x)
def merge_boxes(box1, box2):
    x1, y1 = get_coords(box1)
    x2, y2 = get_coords(box2)

    w1, l1 = get_size(box1)
    w2, l2 = get_size(box2)

    x = min(x1, x2)
    y = min(y1, y2)

    w = max(x1 + w1, x2 + w2) - x
    l = max(y1 + l1, y2 + l2) - y

    return (x, y, w, l)


def get_obstacles_data(outlines, image, terrain_width, terrain_height, rules_name):
    obstacles = []

    # Set base data for each obstacle
    index = len(outlines) - 1
    for outline in outlines:
        box = cv2.minAreaRect(outline)
        box = np.intp(cv2.boxPoints(box))

        # Get the coordinates of the obstacle
        x, y = get_coords(box)
        w, l = get_size(box)

        # Detection bugs
        if w < 0.3 or l < 0.5:
            continue

        # Convert to meters
        x = round((x / image.shape[1]) * terrain_width, 2)
        y = round(((y / image.shape[0]) * terrain_height), 2)
        w = round(((w / image.shape[1]) * terrain_width), 2)
        l = round(((l / image.shape[0]) * terrain_height), 2)

        rulesFile = open(f"{os.getcwd()}/rules/{rules_name}.json")
        rules: dict = json.loads(rulesFile.read())

        obstacles.append({
            "id": index,
            "originX": x,
            "originY": y,
            "centerX": x + w // 2,
            "centerY": y + l // 2,
            "width": w,
            "height": rules.get('height'),
            "length": l,
            "rotation": round(get_rotation(outline), 2)
        })
        index -= 1

    # Determine the smallest obstacle width
    min_width = min(obstacles, key=lambda x: x["width"])["width"]

    for obstacle in obstacles:
        # Vertical obstacles
        if (obstacle["width"] == min_width and obstacle["rotation"] == 0) or (obstacle["length"] == min_width and abs(obstacle["rotation"]) == 90):
            obstacle["type"] = "vertical"

        # Oxers
        elif (obstacle["width"] <= min_width * 1.5 and obstacle["width"] > min_width and obstacle["rotation"] == 0) or (obstacle["length"] <= min_width * 2 and obstacle["length"] > min_width and abs(obstacle["rotation"]) == 90):
            obstacle["type"] = "oxer"

        else:
            obstacle["type"] = "other"

    return obstacles

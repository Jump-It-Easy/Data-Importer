import cv2
import numpy as np
import math


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

    return angle + 90


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


def get_obstacles_data(outlines, image, terrain_width, terrain_height):
    obstacles = []

    # Set base data for each obstacle
    index = len(outlines) - 1
    skip_next = False # In case we have merge him with the tested obstacle
    for outline in outlines:
        box = cv2.minAreaRect(outline)
        box = np.intp(cv2.boxPoints(box))

        # Get the coordinates of the obstacle
        x, y = get_coords(box)
        w, l = get_size(box)

        # TOO LARGE
        # if w > 7 and l > 7:
        #     print("HERE")
        #     continue

        # Merge the obstacle with the next one if they are close
        if not skip_next:
            print("PASSED")
            # for nextOutline in outlines[index + 1:]:
            #     nextBox = cv2.minAreaRect(nextOutline)
            #     nextBox = np.intp(cv2.boxPoints(nextBox))

            #     nextX, nextY = GetCoords(nextBox)
            #     nextW, nextL = GetSize(nextBox)

            #     if GetDistance((x, y), (nextX, nextY)) < 10:
            #         box = mergeBoxes(box, nextBox)
            #         x, y = GetCoords(box)
            #         w, l = GetSize(box)
            #         skipNext = True
            #         break

            # Convert to meters
            x = (x / image.shape[1]) * terrain_width
            print("x == ", x)
            y = (y / image.shape[0]) * terrain_height
            w = (w / image.shape[1]) * terrain_width
            l = (l / image.shape[0]) * terrain_height

            obstacles.append({
                "id": index,
                "originX": x,
                "originY": y,
                "centerX": x + w // 2,
                "centerY": y + l // 2,
                "width": w,
                "length": l,
                "rotation": get_rotation(outline)
            })
            index -= 1

    # Determine the smallest obstacle width
    print(obstacles)
    min_width = min(obstacles, key=lambda x: x["width"])["width"]

    for obstacle in obstacles:
        # Natural obstacles (rock, tree, etc.)
        if obstacle["width"] < 3 and obstacle["length"] < 3:
            obstacle["type"] = "natural"

        # Vertical obstacles
        if (obstacle["width"] == min_width and obstacle["rotation"] == 0) or (obstacle["length"] == min_width and abs(obstacle["rotation"]) == 90):
            obstacle["type"] = "vertical"

        # Oxers
        elif (obstacle["width"] <= min_width * 1.5 and obstacle["width"] > min_width and obstacle["rotation"] == 0) or (obstacle["length"] <= min_width * 2 and obstacle["length"] > min_width and abs(obstacle["rotation"]) == 90):
            obstacle["type"] = "oxer"

    return obstacles

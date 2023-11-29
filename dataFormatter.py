import cv2
import numpy as np
import math


def GetDistance(point1, point2):
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)


def GetRotation(outline):
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


def GetCoords(box):
    x = math.inf
    y = math.inf

    for coords in box:
        if coords[0] < x:
            x = coords[0]
        if coords[1] < y:
            y = coords[1]

    return (x, y)


def GetSize(box):
    if GetDistance(box[0], box[1]) > GetDistance(box[1], box[2]):
        width = GetDistance(box[1], box[2])
        length = GetDistance(box[0], box[1])
    else:
        width = GetDistance(box[0], box[1])
        length = GetDistance(box[1], box[2])

    return (width, length)


# Ne peut pas marcher x)
def mergeBoxes(box1, box2):
    x1, y1 = GetCoords(box1)
    x2, y2 = GetCoords(box2)

    w1, l1 = GetSize(box1)
    w2, l2 = GetSize(box2)

    x = min(x1, x2)
    y = min(y1, y2)

    w = max(x1 + w1, x2 + w2) - x
    l = max(y1 + l1, y2 + l2) - y

    return (x, y, w, l)


def GetObstaclesData(outlines, image, terrainWidth, terrainHeight):
    obstacles = []

    # Set base data for each obstacle
    index = len(outlines) - 1
    skipNext = False  # In case we have merge him with the tested obstacle
    for outline in outlines:
        box = cv2.minAreaRect(outline)
        box = np.intp(cv2.boxPoints(box))

        # Get the coordinates of the obstacle
        x, y = GetCoords(box)
        w, l = GetSize(box)

        # TOO LARGE
        if w > 10 or l > 10:
            continue

        # Merge the obstacle with the next one if they are close
        if not skipNext:
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
            x = (x / image.shape[1]) * terrainWidth
            y = (y / image.shape[0]) * terrainHeight
            w = (w / image.shape[1]) * terrainWidth
            l = (l / image.shape[0]) * terrainHeight

            obstacles.append({
                "id": index,
                "originX": x,
                "originY": y,
                "centerX": x + w // 2,
                "centerY": y + l // 2,
                "width": w,
                "length": l,
                "rotation": GetRotation(outline)
            })
            index -= 1

    # Determine the smallest obstacle width
    minWidth = min(obstacles, key=lambda x: x["width"])["width"]

    for obstacle in obstacles:
        # Natural obstacles (rock, tree, etc.)
        if obstacle["width"] < 3 and obstacle["length"] < 3:
            obstacle["type"] = "natural"

        # Vertical obstacles
        if (obstacle["width"] == minWidth and obstacle["rotation"] == 0) or (obstacle["length"] == minWidth and abs(obstacle["rotation"]) == 90):
            obstacle["type"] = "vertical"

        # Oxers
        elif (obstacle["width"] <= minWidth * 1.5 and obstacle["width"] > minWidth and obstacle["rotation"] == 0) or (obstacle["length"] <= minWidth * 2 and obstacle["length"] > minWidth and abs(obstacle["rotation"]) == 90):
            obstacle["type"] = "oxer"

    return obstacles

import os
import cv2
import numpy as np
import pandas as pd


def GetOutlines(image):
    # Convert to grayscale
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply threshold
    threshold = cv2.threshold(grayscale, 220, 255, cv2.THRESH_BINARY_INV)[1]

    # Find outlines
    outlines, _ = cv2.findContours(
        threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    result = []
    # Filter outlines by size to avoid noise
    for outline in outlines:
        (_, _, w, h) = cv2.boundingRect(outline)

        if w > 10 or h > 10:
            result.append(outline)

    return result


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


def GetObstaclesData(outlines, terrainWidth, terrainHeight):
    obstacles = []
    for outline in outlines:
        (x, y, w, h) = cv2.boundingRect(outline)

        # Convert to meters
        x = (x / image.shape[1]) * terrainWidth
        y = (y / image.shape[0]) * terrainHeight
        w = (w / image.shape[1]) * terrainWidth
        h = (h / image.shape[0]) * terrainHeight

        obstacles.append({
            "originX": x,
            "originY": y,
            "centerX": x + w // 2,
            "centerY": y + h // 2,
            "width": w,
            "length": h,
            "rotation": GetRotation(outline)
        })

    return obstacles


def saveInXlsx(obstacles, imageName):
    xlsxName = imageName.rsplit('/', 1)[0]  # Remove path
    xlsxName = imageName.rsplit('.', 1)[0] + ".xlsx"  # Change file extension

    try:
        pd.DataFrame(obstacles[::-1]).to_excel(
            f"{os.getcwd()}/{xlsxName}", header=True, index=False)
    except:
        print(
            f"A file named {xlsxName}.xlsx exist and is already opened.")
        exit()


def renderResult(image, outlines):
    for outline in outlines:
        box = cv2.minAreaRect(outline)
        box = np.intp(cv2.boxPoints(box))
        cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    showResult = input("Show result ? (Y/n): ").lower() != "n"
    saveInExcel = input("Save in excel ? (Y/n): ").lower() != "n"
    imageName = input("Type the image name (with his extension): ")
    terrainWidth = int(input("Type the terrain width (meters): "))
    terrainHeight = int(input("Type the terrain height (meters): "))

    # Load image
    image = cv2.imread(imageName)

    # Get outlines
    outlines = GetOutlines(image)
    print(f"Obstacles found: {len(outlines)}")

    # Save in a excel file | Show result
    if saveInExcel:
        saveInXlsx(GetObstaclesData(
            outlines, terrainWidth, terrainHeight), imageName)
    if showResult:
        renderResult(image, outlines)

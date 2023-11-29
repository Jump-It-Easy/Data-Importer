import os
import cv2
import numpy as np
import pandas as pd
import dataFormatter
import imageFormatter


def GetOutlines(image):
    # Apply threshold
    threshold = cv2.threshold(image, 220, 255, cv2.THRESH_BINARY_INV)[1]

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
        cv2.drawContours(image, [box], -1, (0, 0, 255), 2)

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

    # Format image
    image = imageFormatter.removeGrid(image)
    image = imageFormatter.cropImage(image)

    # Get outlines
    outlines = GetOutlines(image)

    # Get obstacles data
    obstacles = dataFormatter.GetObstaclesData(
        outlines, image, terrainWidth, terrainHeight)
    print(f"Obstacles found: {len(obstacles)}")

    # Save in a excel file | Show result
    if saveInExcel:
        saveInXlsx(obstacles, imageName)
    if showResult:
        renderResult(image, outlines)

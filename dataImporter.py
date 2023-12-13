import os
import json
import cv2
import numpy as np
import pandas as pd
import dataFormatter
import imageFormatter
import schemaValidator


def get_outlines(image):
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


def save_in_json(obstacles):
    try:
        jsonResult = json.dumps(pd.DataFrame(
            obstacles[::-1]).to_dict(orient='records'))
        open(f"{os.getcwd()}/temp/temp_schema.json", 'w').write(jsonResult)
    except Exception as e:
        print(e)
        exit(1)


def save_in_xlsx(obstacles, image_name: str):
    file_name = image_name.rsplit('/', 1)[0].rsplit('.', 1)[0]  # Remove path

    try:
        pd.DataFrame(obstacles[::-1]).to_excel(
            f"{os.getcwd()}/{file_name}.xlsx", header=True, index=False)
    except Exception as e:
        print(e)
        exit(1)


def render_result(image, outlines):

    for outline in outlines:
        box = cv2.minAreaRect(outline)
        box = np.intp(cv2.boxPoints(box))
        cv2.drawContours(image, [box], -1, (0, 0, 255), 2)

    cv2.imshow("Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    show_result = input("Show result ? (Y/n): ").lower() != "n"
    save_in_excel = input("Save in excel ? (Y/n): ").lower() != "n"
    image_name = input("Type the image name (with his extension): ")
    terrain_width = int(input("Type the terrain width (meters): "))
    terrain_height = int(input("Type the terrain height (meters): "))
    rule_name = input("What's the desired level ? (club1, club2, etc..): ")

    # Load image
    image = cv2.imread(image_name)

    # Format image
    image = imageFormatter.remove_grid(image)
    image = imageFormatter.crop_image(image)

    # Get outlines
    outlines = get_outlines(image)

    # Get obstacles data
    obstacles = dataFormatter.get_obstacles_data(
        outlines, image, terrain_width, terrain_height, rule_name)
    print(f"Obstacles found: {len(obstacles)}")

    save_in_json(obstacles)

    valid = schemaValidator.validate_schema(rule_name)

    if not valid:
        exit(1)

    # Save in a excel file | Show result
    if save_in_excel:
        save_in_xlsx(obstacles, image_name)
    if show_result:
        render_result(image, outlines)

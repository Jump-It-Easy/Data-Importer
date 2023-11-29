import cv2
import numpy as np
import dataImporter


def remove_grid(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    return image


def crop_image(image):
    box = dataImporter.get_outlines(image)[0]
    box = cv2.minAreaRect(box)
    box_size = np.intp(cv2.boxPoints(box))
    return image[box_size[0][1]+10:box_size[2][1]-10, box_size[0][0]+10:box_size[2][0]-10]

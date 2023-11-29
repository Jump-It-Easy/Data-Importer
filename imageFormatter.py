import cv2
import numpy as np
import dataImporter


def removeGrid(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    return image


def cropImage(image):
    box = dataImporter.GetOutlines(image)[0]
    box = cv2.minAreaRect(box)
    boxSize = np.intp(cv2.boxPoints(box))
    return image[boxSize[0][1]+10:boxSize[2][1]-10, boxSize[0][0]+10:boxSize[2][0]-10]

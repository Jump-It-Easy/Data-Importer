import cv2
import pandas as pd

showResult = input("Show result ? (y/n): ").lower() == "y"
saveInExcel = input("Save in excel ? (y/n): ").lower() == "y"
imageName = "images/" + input("Type the image name (with his extension): ")

image = cv2.imread(imageName)

# Convert to grayscale
grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply Canny filter to detect edges
edges = cv2.Canny(grayscale, 100, 255)
edges = cv2.threshold(edges, 100, 255, cv2.THRESH_BINARY)[1]

# Find contours
contours, hierarchy = cv2.findContours(
    edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

obstacles = []

# Review & filter contours
finalContours = []
for contour in contours:
    (x, y, w, h) = cv2.boundingRect(contour)

    if (w > 10 or h > 10):
        # Get center of the contours
        center = (x + w // 2, y + h // 2)

        finalContours.append(contour)

        obstacles.append({
            "originX": x,
            "originY": y,
            "centerX": center[0],
            "centerY": center[1],
            "width": w,
            "height": h
        })

# Save obstacles in excel
if saveInExcel:
    try:
        pd.DataFrame(obstacles).to_excel(
            f"{imageName.rsplit('.', 1)[0]}.xlsx", header=True, index=False)
    except:
        print(
            f"A file named {imageName.rsplit('.', 1)[0]}.xlsx exist and is already opened.")
        exit()

# Show result image in a window
if showResult:
    cv2.drawContours(image, finalContours, -1, (0, 255, 0), 2)
    cv2.imshow("Image", image)
    cv2.waitKey(0)
print(f"Obstacles found: {len(finalContours)}")

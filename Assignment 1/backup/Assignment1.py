import math
import cv2
import numpy as np

# Function to convert millimeters to inches
def convert_milli_to_inch(x):
    # This function assumes 'x' is in millimeters (mm)
    return x / 25.4

def calculate_dimensions_from_image():
    # --- YOUR IMAGE PATH ---
    image_path = "ObjectImage.JPG"

    # Read the image from the specified file path
    image = cv2.imread(image_path)

    # Check if the image was read successfully
    if image is None:
        print(f"Error: Failed to read the image from {image_path}. Make sure the file exists.")
        return

    print("Image loaded successfully. Please select the object's ROI.")

    # Select ROI
    roi = cv2.selectROI("Select ROI", image)
    x, y, w, h = roi

    if w == 0 or h == 0:
        print("No ROI selected. Exiting.")
        return

    print(f"Selected ROI: (x={x}, y={y}, w={w}, h={h})")

    # parameters
    FX = 4124.85217000
    FY = 4126.41606000
    cx = 2774.74600000
    cy = 2302.01489000

    # Set the measured distance to the object
    Z = 300  # In millimeters (e.g., 30cm)

    # Calculate the real-world dimensions
    # First, calculate the real-world coordinates of the top-left and bottom-right points
    Real_point1x = (x - cx) * Z / FX
    Real_point1y = (y - cy) * Z / FY
    Real_point2x = ((x + w) - cx) * Z / FX
    Real_point2y = ((y + h) - cy) * Z / FY

    # Then, find the difference to get the width and height
    real_width_mm = abs(Real_point2x - Real_point1x)
    real_height_mm = abs(Real_point2y - Real_point1y)

    # Convert width and height to inches for display
    width_inches = convert_milli_to_inch(real_width_mm)
    height_inches = convert_milli_to_inch(real_height_mm)

    print(f"Calculated Real-World Width: {real_width_mm:.2f} mm ({width_inches:.2f} inches)")
    print(f"Calculated Real-World Height: {real_height_mm:.2f} mm ({height_inches:.2f} inches)")

    # --- Visualization on the image ---
    # Draw the selected ROI on the image
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Add text with the dimensions
    text_width = f"W: {real_width_mm:.2f} mm"
    text_height = f"H: {real_height_mm:.2f} mm"
    cv2.putText(image, text_width, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(image, text_height, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Define the output file path
    output_image_path = "annotated_image.png"
    cv2.imwrite(output_image_path, image)

    # Display the image with annotations
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)

    cv2.imshow("Annotated Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print(f"Annotated image saved as: {output_image_path}")

calculate_dimensions_from_image()
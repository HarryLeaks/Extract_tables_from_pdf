from pdf2image import convert_from_path
import os
import pytesseract
from pytesseract import Output
import cv2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import pandas as pd
import numpy as np
from paddleocr import PPStructure,save_structure_res

def convert_pdf_to_img(file):
    images = convert_from_path(file)
    image_filenames = []
    for i, image in enumerate(images, start=1):
        filename = f"{i}.jpg"
        image.save(filename, "JPEG")
        image_filenames.append(filename)
    return image_filenames

'''def convert_image_to_pdf(image_path, pdf_path):
    # Open the image using Pillow
    img = Image.open(image_path)

    # Create a PDF file
    pdf_canvas = canvas.Canvas(pdf_path, pagesize=letter)

    # Calculate aspect ratio to maintain image proportions
    width, height = letter
    aspect_ratio = img.width / img.height

    # Calculate the width and height to fit the image on the page
    if aspect_ratio > 1:
        new_width = width
        new_height = width / aspect_ratio
    else:
        new_width = height * aspect_ratio
        new_height = height

    # Center the image on the page
    x_offset = (width - new_width) / 2
    y_offset = (height - new_height) / 2

    # Draw the image on the PDF canvas
    pdf_canvas.drawInlineImage(img, x_offset, y_offset, width=new_width, height=new_height)

    # Save the PDF file
    pdf_canvas.save()'''

# Define img as a global variable
img = None
counter = 0
coordinates_list = []

def cropped_image(file, coordinates):
    global img  # Add this line to use the global variable
    image = cv2.imread(file)

    # Extract coordinates from the list
    x1, y1 = coordinates[0]
    x2, y2 = coordinates[1]
    x3, y3 = coordinates[2]
    x4, y4 = coordinates[3]

    # Find the minimum and maximum x, y values
    min_x = min(x1, x2, x3, x4)
    max_x = max(x1, x2, x3, x4)
    min_y = min(y1, y2, y3, y4)
    max_y = max(y1, y2, y3, y4)

    # Crop the image using the coordinates
    cropped_image = image[min_y:(max_y + 1), min_x:(max_x + 1)]
    cv2.imwrite("cropped_" + file, cropped_image)

def click_event(event, x, y, flags, params):
    global img, counter, coordinates_list  # Add this line to use the global variable
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'({x},{y})')

        # put coordinates as text on the image
        cv2.putText(img, f'({x},{y})', (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # draw point on the image
        cv2.circle(img, (x, y), 3, (0, 255, 255), -1)

        # Add coordinates to the list
        coordinates_list.append((x, y))
        counter += 1

def Dimension(file):
    global img, counter, coordinates_list  # Add this line to use the global variable
    # read the input image
    img = cv2.imread(file)

    if img is None:
        print(f"Error: Unable to read the image file '{file}'")
        return

    # create a window
    cv2.namedWindow('Point Coordinates')
    # bind the callback function to window
    cv2.setMouseCallback('Point Coordinates', click_event)

    # display the image
    while counter < 4:
        cv2.imshow('Point Coordinates', img)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()

    # Call the cropped_image function with the coordinates_list
    if len(coordinates_list) == 4:
        cropped_image(file, coordinates_list)

def main():
    global coordinates_list, counter
    file = "BankStatement.pdf"
    image_filenames = convert_pdf_to_img(file)

    # Iterate over pages and ask the user whether to crop or not
    for i, image_filename in enumerate(image_filenames, start=1):
        print(f"\nProcessing page {i}")
        
        # Ask the user if they want to crop this page
        answer = input("Do you want to crop this page? (y/n): ").lower()
        
        if answer == 'y':
            print("Select 4 points on the image for cropping:")
            Dimension(image_filename)
            
            # Assuming 'cropped_image_path' is the path where you saved the cropped image
            cropped_image_path = f"cropped_{image_filename}"
            
            # Check if the cropped image file exists
            if os.path.isfile(cropped_image_path):
                table_engine = PPStructure(layout=False, show_log=True)
                save_folder = './output'
                img = cv2.imread(cropped_image_path)
                result = table_engine(img)
                save_structure_res(result, save_folder, os.path.basename(cropped_image_path).split('.')[0])

                for line in result:
                    line.pop('img')
                    print(line)
                    
            else:
                print(f"Cropped image file '{cropped_image_path}' not found.")
            
            coordinates_list = []
            counter = 0
        else:
            print("Skipped cropping for this page.")



if __name__ == "__main__":
    main()

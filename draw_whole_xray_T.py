import deepdrr
from deepdrr import geo
from deepdrr.projector import Projector
import numpy as np
import matplotlib.pyplot as plt
from skimage import exposure

# Load the patient volume
patient = deepdrr.Volume.from_nifti("sample_datasets/case-100114_BONE_TORSO_3_X_3.nii.gz", use_thresholding=True)
patient.facedown()
lower, top = patient.get_bounding_box_in_world()

# Define the common parameters
x, y, z = -100, 24.6245, 66.4077
a, b = 0, 0
half_center = (top[1] - lower[1]) / 3
positions_hor = [half_center, 0, -half_center]

multiply = 0
center_x = patient.center_in_world[0]
for i in range(0, 10):
    center_x = center_x - half_center
    multiply += 1
    if center_x < lower[0]:
        break
    
positions_ver = [i * half_center for i in range(-multiply, multiply + 1)]

# Function to generate projection images
def get_projection_image(offset_x, offset_y):
    carm = deepdrr.MobileCArm(patient.center_in_world + geo.v(offset_x, offset_y, 0), 
                              alpha=-np.rad2deg(a), beta=-np.rad2deg(b))
    with Projector(patient, carm=carm) as projector:
        image = projector()
        image = exposure.equalize_adapthist(image / np.max(image), clip_limit=0.03)
    return image

# Generate the images
images = [[get_projection_image(pos_x, pos_y) for pos_y in positions_hor] for pos_x in positions_ver]

# Calculate the total width and the maximum height for the combined image
heights, widths = (images[0][0].shape[0] * len(positions_ver), images[0][0].shape[1] * len(positions_hor))

# Create a new blank array with the calculated width and height
combined_image = np.zeros((heights, widths), dtype=images[0][0].dtype)

# Paste the images into the new array
y_offset = 0
for img_line in images:
    x_offset = 0
    for img in img_line:
        combined_image[y_offset:y_offset+img.shape[0], x_offset:x_offset+img.shape[1]] = img
        x_offset += img.shape[1]
    y_offset += img.shape[0]

coordinates = [
    [-371.938, -145.711, 66.4077],
    [-369.048, 189.347, 66.4077],
    [-334.787, -110.142, 66.4077],
    [-334.944, 125.794, 66.4077],
    [-368.17, 5.5514, 66.4077],
    [-297.279, -10.6617, 66.4077],
    [-102.429, -3.85235, 66.4077],
    [89.3476, -6.34998, 66.4077],
    [38.6821, -87.8765, 66.4077],
    [45.1486, 76.4634, 66.4077],
    [201.201, -11.7334, 66.4077],
    [181.864, -95.8285, 66.4077],
    [182.994, 77.46, 66.4077]
]

landmarks = [2, 3, 4, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18]


# Ratio for scaling coordinates
ratio = widths / (top[1] - lower[1])

# Plot the combined image
plt.figure(figsize=(10, 10))
plt.imshow(combined_image, cmap='gray')
plt.axis('off')  # Turn off axis

# Draw squares and add text labels for each landmark
for landmark, coordinate in zip(landmarks, coordinates):
    converted_x = coordinate[1] * ratio
    converted_y = coordinate[0] * ratio

    # Define the position and size of the square (in this example, centered and 1/3 of the image size)
    square_center_x = combined_image.shape[1] // 2
    square_center_y = combined_image.shape[0] // 2
    square_size = min(combined_image.shape[0], combined_image.shape[1]) // 5

    # Draw the square
    square = plt.Rectangle(((square_center_x + converted_x) - square_size // 2, (square_center_y + converted_y) - square_size // 2), 
                        square_size, square_size, 
                        linewidth=2, edgecolor='r', facecolor='none')
    plt.gca().add_patch(square)

    # Add text label inside the square
    plt.text((square_center_x + converted_x) - square_size // 4, (square_center_y + converted_y), f'{landmark}', color='blue',fontsize=15, ha='center', va='center')

# Collect all dot coordinates
dot_coordinates_x = [(coordinate[1] * ratio) + (combined_image.shape[1] // 2) for coordinate in coordinates]
dot_coordinates_y = [(coordinate[0] * ratio) + (combined_image.shape[0] // 2) for coordinate in coordinates]

# Draw all dots in one go
plt.plot(dot_coordinates_x, dot_coordinates_y, 'ro')  # 'ro' means red color, circle marker

# Save the image with the squares and dots
plt.savefig("combined_samples_T.jpg", bbox_inches='tight', pad_inches=0, dpi=300)
plt.show()
import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Define Arduino serial port and baudrate
arduino_port = 'COM6'  # Change this to your Arduino port
baudrate = 115200
matrix_size = (15, 15)  # Define matrix size

# Create a colormap with visually appealing colors
def create_custom_colormap():
    # Define colors for ranges of 100 units each
    colors = [
        (0.0, 0.0, 0.3),  # 0-99 Dark Blue
        (0.0, 0.0, 0.7),  # 100-199 Blue
        (0.0, 0.5, 1.0),  # 200-299 Light Blue
        (0.0, 1.0, 0.5),  # 300-399 Cyan
        (0.5, 1.0, 0.0),  # 400-499 Green
        (1.0, 1.0, 0.0),  # 500-599 Yellow
        (1.0, 0.5, 0.0),  # 600-699 Orange
        (1.0, 0.0, 0.0),  # 700-799 Red
        (0.5, 0.0, 0.0),  # 800-899 Dark Red
        (0.3, 0.0, 0.0),  # 900-999 Darkest Red
        (0.1, 0.0, 0.0)   # 1000-1023 Almost Black
    ]
    return LinearSegmentedColormap.from_list("custom_cmap", colors, N=1024)

cmap = create_custom_colormap()

def read_data_from_arduino():
    # Open the serial port
    arduino = serial.Serial(arduino_port, baudrate, timeout=1)
    # Wait for Arduino to reset
    time.sleep(2)
    # Initialize an empty list to store the rows of the matrix
    matrix_rows = []
    # Read data from Arduino for each row
    for _ in range(matrix_size[0]):
        row_data = arduino.readline().decode('utf-8').strip()
        if row_data:  # Check if the row_data is not empty
            # Split the row data into individual values using '\t' as the delimiter
            row_values = list(map(float, row_data.split('\t')))
            # Append the row to the list of matrix rows
            matrix_rows.append(row_values)
        else:
            print("Waiting for data....")
    arduino.close()  # Close the serial port
    # Convert the list of rows into a 2D NumPy array
    matrix = np.array(matrix_rows)

    # Divide the matrix into parts
    L1 = matrix[10:13, 2:6]
    L2 = matrix[6:9, 2:6]
    L12 = matrix[8:9, 2:6]
    L3 = matrix[2:6, 2:6]
    R1 = matrix[10:13, 9:13]
    R12 = matrix[8:9, 9:13]
    R2 = matrix[6:9, 9:13]
    R3 = matrix[2:6, 9:13]

    return matrix, L1, L2, L12, L3, R1, R12, R2, R3

def display_heatmap(matrix):
    global previous_matrix
    if not np.array_equal(matrix, previous_matrix):
        plt.clf()  # Clear the previous plot
        plt.imshow(matrix, cmap=cmap, interpolation='nearest', vmin=0, vmax=1023, aspect='equal')
        plt.colorbar()
        plt.title('Arduino Matrix Heatmap')
        plt.xlabel('Row')  # Correctly label rows
        plt.ylabel('Column')  # Correctly label columns
        plt.xticks(np.arange(matrix_size[1]), np.arange(matrix_size[1]))  # Set x-axis labels
        plt.yticks(np.arange(matrix_size[0]), np.arange(matrix_size[0]))  # Set y-axis labels up to 14
        plt.gca().set_aspect('equal', adjustable='box')  # Maintain 1:1 aspect ratio
        plt.gca().invert_yaxis()  # Invert y-axis to have 0 at the bottom
        plt.pause(0.01)  # Pause to allow time for the plot to update
        previous_matrix = np.copy(matrix)

if __name__ == '__main__':
    previous_matrix = np.zeros(matrix_size)  # Initialize previous matrix
    plt.ion()  # Turn on interactive mode
    plt.figure(figsize=(5, 5))  # Create a new figure with a square aspect ratio

    while True:
        # Read data from Arduino
        arduino_matrix, L1, L2, L12, L3, R1, R12, R2, R3 = read_data_from_arduino()

        # Display the received matrix as a heatmap if different from previous
        display_heatmap(arduino_matrix)

        # Check each part for activity and print alphanumeric if active
        L1_active = np.any(L1 > 300)
        L2_active = np.any(L2 > 300)
        L3_active = np.any(L3 > 300)
        R1_active = np.any(R1 > 300)
        R2_active = np.any(R2 > 300)
        R3_active = np.any(R3 > 300)

        if L1_active and L2_active and L3_active and not (R1_active or R2_active or R3_active):
            print("Left leg in normal stance")
        elif R1_active and R2_active and R3_active and not (L1_active or L2_active or L3_active):
            print("Right leg in normal stance")
        elif L1_active and L2_active and L3_active and R1_active and R2_active and R3_active:
            print("Normal stance")
        elif L1_active and R1_active and not (L2_active or L3_active or R2_active or R3_active):
            print("Tip toed")
        elif L1_active and not (L2_active or L3_active or R1_active or R2_active or R3_active):
            print("Left leg is tip toed")
        elif R1_active and not (L1_active or L2_active or L3_active or R2_active or R3_active):
            print("Right leg is tip toed")
        elif R3_active and not (L1_active or L2_active or L3_active or R1_active or R2_active):
            print("Right leg is in heel standing position")
        elif L3_active and not (L1_active or L2_active or R1_active or R2_active or R3_active):
            print("Left leg is in heel standing position")
        elif L3_active and R3_active:
            print("Heel standing")


        # Allow some time for the GUI event loop to process
        plt.pause(0.001)
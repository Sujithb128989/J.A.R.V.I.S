import os

# Define the function to get the path to the Graphics directory
def GraphicsDirectoryPath(Filename):
    current_dir = os.getcwd()  # Get the current working directory
    GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")
    Path = os.path.join(GraphicsDirPath, Filename)  # Combine the GraphicsDirPath and the filename
    return Path

# Check if the 'close.png' file exists in the Graphics directory
file_path = GraphicsDirectoryPath('close.png')

# Print the result
if os.path.exists(file_path):
    print(f"File exists: {file_path}")
else:
    print(f"File does not exist: {file_path}")

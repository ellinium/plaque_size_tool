# Bacteriophage plaques size tool
This Python 3 tool takes Petri dish images as input and measures the sizes of the bacteriophage round and oval-shaped plaques.

# Installation

## Installation using pip 
The following command should be executed:
```
pip install plaque-size-tool
```

## Upgrade using pip 
Upgrade an already installed package to the latest from PyPI:
```
pip install --upgrade plaque-size-tool
```

## Prerequisites
1.  Python 3.6 or higher should be installed in the system:

    For Python 3 installation, please navigate to https://www.python.org/downloads/.
    The detailed instructions for download and installation are provided at  https://wiki.python.org/moin/BeginnersGuide/Download.

2. PIP should be installed in the system:

    pip is already installed if you are using Python 2 >=2.7.9 or Python 3 >=3.4 downloaded from python.org.
    If it is not installed, please navigate to https://pip.pypa.io/en/stable/installing/ for the instructions.


By default the tool will be installed into the directories depending on the OS:

Please see https://docs.python.org/3/install/ for the details.
# Usage

The tool supports TIF, TIFF, JPG, JPEG and PNG image formats.

## Run the tool
To run the tool, use one of the following options. The output will be placed into `./out` directory of the project.

### on a file
If it's required to analyze a single file, run the following command:
```
python plaque_size_tool.py -i <path_to_the_file> [-p plate_size] [-small]
```
### on a directory
If it's required to analyze multiple files, put all files in the directory. Then run the following command:
```
python plaque_size_tool.py -d <path_to_the_directory> [-p plate_size] [-small]
```
## Additional options
```
-p plate_size - (Optional) Petri dish size (mm). If not specified all measurements are taken in pixels.
-small - (Optional) Use on plates with small plaques (less than 2.5 mm) 
``` 
##Examples
```
python plaque_size_tool.py -i Test_plates/large/29.tif -p 90
python plaque_size_tool.py -i Test_plates/small/7.tif -p 90 -small

```
## Output
The tool produces two output files:
```
1. out_<file_name> - an image with valid plaques circled with green colour, where <file_name> is the name of the original file

2. data-green-<file_name>.csv - a CSV file with detected plaques parameters: 
INDEX_COL - the ID of the plaque that corresponds to the ID on the output image
AREA_PXL - Area of a plaque in pixels
PERIMETER - Perimeter of a plaque in pixels
AREA_MM2 -  Area of a plaque in millimiters if plate size is specified
AREA_MM2 -  Area of a plaque in millimiters squared if plate size is specified
DIAMETER_MM - Diameter of a plaque in millimiters if plate size is specified    
```

## Notes
This tool was tested on grey images in TIF format made using a Bio-Rad GelDoc system with the Exposure parameter equal to 0.750 sec.
The tool can automatically adjust brightness and contrast of images for processing.
If you are experiencing any issues with your images (for example, overprocessing), please email to [ellina.trofimova@hdr.mq.edu.au](mailto:ellina.trofimova@hdr.mq.edu.au) with a copy to [ellina.trofimova@gmail.com](mailto:ellina.trofimova@gmail.com)

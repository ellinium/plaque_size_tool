# Bacteriophage plaques size tool
This Python 3 Plaque Size Tool (or PST) takes Petri dish images as input and measures the size of the bacteriophage round and oval-shaped plaques.

# Installation

## Step 1. Download the archive from GitHub
Navigate to https://github.com/ellinium/plaque_size_tool.
After that, click the green button 'Code' in the right corner and select the option 'download zip'.
Unpack the archive into the directory of your choice.

If you have the installed git another option to download the files is to use the command:
```
git clone https://github.com/ellinium/plaque_size_tool
```

## Step 2. Installation using pip 
This command will install the libraries required for Plaque Size Tool into the system directories.
```
pip install plaque-size-tool
```

## Prerequisites
1.  Python 3.6 or higher should be installed in the system:

    For Python 3 installation, please navigate to https://www.python.org/downloads/.
    The detailed instructions for download and installation are provided at https://wiki.python.org/moin/BeginnersGuide/Download.

2. PIP should be installed in the system:

    pip is usually already installed if you are using Python 2 >=2.7.9 or Python 3 >=3.4 downloaded from python.org.
    If it is not installed, please navigate to https://pip.pypa.io/en/stable/installing/ for the instructions (see the section 'Installing with get-pip.py', where it is required to download get-pip.py and install pip using the command:
```
python get-pip.py
```

Note: if you have several versions of python in the system use python3 in all specified commands.


# Usage

The tool supports TIF, TIFF, JPG, JPEG and PNG image formats.

## Run the tool
To run the tool, use one of the two options specified bellow. The output will be placed into `./out` directory of the project.
You can execute the command from the directory used in Installation Step 1.
If your current directory differs, you need to include a full path to the tool.

### on a file
If it's required to analyze a single file, run the following command:
```
python plaque_size_tool.py -i <path_to_the_file> [-p plate_size] [-small]

or

python PATH_TO_PST/plaque_size_tool.py -i <path_to_the_file> [-p plate_size] [-small]

```
### on a directory
If it's required to analyze multiple files, put all files in the directory. Then run the following command:
```
python plaque_size_tool.py -d <path_to_the_directory> [-p plate_size] [-small]

or

python PATH_TO_PST/plaque_size_tool.py -d <path_to_the_directory> [-p plate_size] [-small]

```
## Additional options
```
-p plate_size - (Optional) Petri dish size (mm). If not specified all measurements are taken in pixels.
-small - (Optional) Use on plates with small plaques (less than 2.5 mm) 
``` 

## Output
The tool produces two output files:
```
1. out_<file_name> - an image with valid plaques circled with green colour, where <file_name> is the name of the original file.
If <p> (plate size) parameter is specified, the results will be shown in mm. If <p> is not specified then in pixels.

2. data-green-<file_name>.csv - a CSV file with detected plaques parameters: 
INDEX_COL - the ID of the plaque that corresponds to the ID on the output image
AREA_PXL - Area of a plaque in pixels
PERIMETER - Perimeter of a plaque in pixels
AREA_MM2 -  Area of a plaque in millimetres if plate size is specified
AREA_MM2 -  Area of a plaque in millimetres squared if plate size is specified
DIAMETER_MM - Diameter of a plaque in millimetres if plate size is specified    
```
## Examples
```
python plaque_size_tool.py -i Test_plates/large/29.tif -p 90  - runs the tool on the file 29.tif that has a plate size 90 mm. The results on a plate will be shown in mm.
python plaque_size_tool.py -i Test_plates/large/29.tif  - runs the tool on the file 29.tif. All results will be shown in pixels as the plate size is not specified.

python plaque_size_tool.py -d Test_plates/small -p 90 -small - runs the tool on the directory Test_plates/small that contains plates with small plaques (<= 2.5 mm). The results on a plate will be shown in mm.

```
## Notes
This tool was tested on grey images in TIF format made using a Bio-Rad GelDoc system with the Exposure parameter equal to 0.750 sec.
The tool can automatically adjust brightness and contrast of images for processing.
If you are experiencing any issues with your images (for example, overprocessing), please email [ellina.trofimova@hdr.mq.edu.au](mailto:ellina.trofimova@hdr.mq.edu.au) with a copy to [ellina.trofimova@gmail.com](mailto:ellina.trofimova@gmail.com).

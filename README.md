# HEC-RAS 2D Steady State Check
> This app checks if each cell in a 2D HEC-RAS model has reached steady state condition and creates a shapefile of the cells with the time to reach steady state condition for each cell. Steady state condition criteria for a cell is defined as when the cell's water surface elevation (WSE) stops changing by a specified amount over a specificd period of time. A common practice is 0.01 feet over an hour of model time. The WSE change and time period can be specified by the user.

Input:
- HDF output file from the HEC-RAS plan that is being analyzed.
- 2D cell polygon shapefile from the geometry that is being analyzed.

Output:
- The 2D cell polygon shapefile that was input but with a field added with the time taken to reach steady state.

## Usage
Currently the app is set to run like a script. The input files need to be saved in the data/ subdirectory. The output file will be saved here too. To run the app:
- create a virtual environment and install the dependancies with "pip install -r requirements.txt"
- Open the HECRAS_2D_SteadyStateCheck.py file
- Update the parameters in lines 13-18 to match your HEC-RAS project.
- Save the HDF output file and 2D cell shapefile in the data/ folder.
- run the main script from the terminal with "python HECRAS_2D_SteadyStateCheck.py"

## Meta

Tom Chingas – tomchingas@gmail.com

Distributed under the  GNU GENERAL PUBLIC LICENSE. See ``LICENSE`` for more information.

[https://github.com/tomchingas]


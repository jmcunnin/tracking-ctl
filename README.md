Megacities-TRACKING
===================

This is a project for the Megacities Logistics Lab at MIT that aims to track trucks based on GPS data.

The project is comprised of two major folders: an example folder that contains the basic structure of how the project should be made up and the python scripts used to track the trucks.

example\_folder: 
-----------------
Shows the basic structure required for the setup. Basically takes all of the unprocessed data input as CSVs and inserts it into processed CSVs and a sqlite database. 

To run on a \*NIX system, run $source master\_script.sh. 

To revert project to completely unprocessed, run $source cleanup.sh. 

General Project Flow:
---------------------
To use this package, the general structure of the given folder must be followed:
Root\_folder:
(Shell Scripts)
-> cleanup.sh
-> master\_script.sh
(Python Scripts)
-> conversion\_script.py
->filter\_jumps.py
->path\_object.py
->tracker.py


Basically, what the package does is, when the master shell script is run, the script stores all of the data from the csv files in the raw\_data folder to the database and files in the processed data folder (Calling conversion\_script.py). Then the script calls the tracker.py object, which computes the stays, warehouses, paths, etc. and stores those values to the database).

To modify search parameters, one must open the master\_script and modify the parameters there.

To run, one must place the files to be investigated in CSV format, into the raw\_data folder. Then, run the command "source master\_script.sh" and the values will be computed and stored to the database in the database folders

If you would like to reset the folder, the folder can be reset using "source cleanup.sh"

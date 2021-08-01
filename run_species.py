import os
import pprint
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import wranglerconfig as config
import wrangler_functions as functions
import time
import csv
import json
import sqlite3
import glob

def make_species_dict(species_name):
    '''
    Creates a species specific dictionary to be used in wildlife
    wrangler function calls ad the "taxon_concept"
    ----------
    species_name : the name of the species to populate dictionary with

    Returns
    -------
    Dictionary holding species specific information.

    Notes
    -------
    Not checking EBIRD at this time
    '''

    species_dict = {}
    species_dict['ID'] = species_name;
    species_dict['GBIF_ID'] = functions.get_GBIF_code(species_name);
    species_dict['EBIRD_ID'] = None
    species_dict['detection_distance_m'] = 200
    species_dict['TAXON_EOO'] = None
    return species_dict

def main():
    """
    Note: This file is used in conjunction with:
       wranglerconfig.py - your filled out version of the included
                           wranglerconfig_TEMPLATE.py file 
       species_file - a CSV file containing a single 'name' column holding
                      scientific names of species for which to obtain GBIF IDs.
                      Must be present in codDir specified in 
                      wranglerconfig.py.
       filters_file - a JSON file that specifies how you want records filtered 
                      and cleaned. Must be present in codDir specified in 
                      wranglerconfig.py.
                  
       After running this script, for each species in your species_file:
       - a sub-directory for will be added to the working directory named 
         in your wranglerconfig.py file.
       - a SQLITE database file obtained from wildlife_wrangler will be placed
         in each subdirectory. The database will hold the filtered species 
         occurrence records with documentation. 

    """
    # working_directory gets passed into get_GBIP_records and process_records
    working_directory = config.workDir + time.strftime("%Y%m%d-%H%M%S") +"\\"
    os.mkdir(working_directory)

    username = config.gbif_username
    password = config.gbif_password
    email = config.gbif_email
    EBD_file = config.EBD_file
    species_file = config.species_filename
    filters_file = config.filters_filename

    #get filter set
    with open(filters_file, "r") as f:
        filter_set = json.load(f)
        f.close()
 
    # Process each  species names in the species file
    with open(species_file, 'r') as f:
        reader = csv.reader(f)
        # skip the header row
        next(reader)
        for row in reader:
            species_dict = make_species_dict(row[0])

        print(species_dict['ID'])

        gbif_data = functions.get_GBIF_records(species_dict, filter_set, species_dict['ID'], working_directory, username, password, email)
        functions.process_records(ebird_data=None, gbif_data=gbif_data, filter_set=filter_set, 
                            taxon_info=species_dict, working_directory=working_directory, 
                            query_name=species_dict['ID'])

        # add species info and filter_set to databasee constructed in process records, above
        con = sqlite3.connect(working_directory + species_dict['ID'] + '.sqlite')
        cursor = con.cursor()
        pd.DataFrame(species_dict.values(), species_dict.keys()).applymap(str).to_sql(name='taxon_concept', con=con, if_exists='replace')
        pd.DataFrame(filter_set.values(), filter_set.keys()).applymap(str).to_sql(name='filter_set', con=con, if_exists='replace')
        con.close()

        # remove the Darwin Core Archive zip file, as it is no longer needed
        for zipfile in glob.iglob(os.path.join(working_directory, '*.zip')):
            os.remove(zipfile)


if __name__ == "__main__":
    main()
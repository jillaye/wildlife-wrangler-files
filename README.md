# wildlife-wrangler-files
Files that interact with Nathan Tarr's wildlife-wrangler framework for collecting and filtering occurrence data

**add_species_to_db.py** - Python script which will add GBIF IDs to to each species in a CSV file and add the species and associated GBIF ID to the taxa_concepts table of the parameters database (wildlife-wrangler.sqlite)\
**call_ww_retrieve.py** - Python script which will create a species database for each species in a CSV file\
**wranglerconfig_TEMPLATE.py** - A copy of the wranglerconfig.py template from wildlife wrangler. Must be filled out before running call_ww_retrieve.py. Note: I added "species_filename" which is the name of the Excel spreadsheet holding names of species to run. Fill out the required items and remove "_TEMPLATE" from the filename.\
**wildlife-wrangler_TEMPLATE.sqlite** - a copy of the wildlife-wrangler.sqlite database. I added GRINFilters and GRINRequests to the gbif_filters and gbif_requests tables, respectively. Remove "_TEMPLATE" from the DB filename.

## Workflow
1. Place all of the files listed above in the **same** directory as your wildlife-wrangler repo.
2. Fill out the required items in wranglerconfig_TEMPLATE.py and remove _TEMPLATE from the name.
3. Remove _TEMPLATE from wildlife-wrangler_TEMPLATE.sqlite.
4. Run add_species_to_db.py
5. Run call_ww_retrieve.py

## Expected Results
1. A species database will be created for each species in your CSV file (species_filename in wranglerconfig.py). These will be saved to your Outputs directory based on your workDir in wranglerconfig.py.
2. Four files needed to define the geometry and attributes of geographically referenced features:
    a. .shp—The main file that stores the feature geometr (required).
    b. .shx—The index file that stores the index of the feature geometry (required).
    c. .dbf—The dBASE table that stores the attribute information of features (required).
    d. .prj—The file that stores the coordinate system information (used by ArcGIS).



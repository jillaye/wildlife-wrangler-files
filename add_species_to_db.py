import pandas as pd
import sqlite3
import wrangler_functions as functions
import wranglerconfig as config

def main():
    """
    Note: This file is used in conjunction with:
       paramdb      - your copy of the wildlife-wrangler.sqlite database
       species_file - a CSV file containing a single 'name' column holding
                      scientific names of species for which to obtain GBIF IDs
                  
       After running this script:
       - a 'gbif_id' column, holding the species GBIF ID, will be added to the species_file
       - an entry for each species in species_file will be added to the taxa_concepts 
         table in paramdb.

    """
    
    # Connect to the parameters database
    paramdb = config.paramdb
    conn = sqlite3.connect(paramdb)
    cursor = conn.cursor()

    # Read the species names from the species file
    species_file = 'Species_GBIF_R1_Test.csv'
    df = pd.read_csv(species_file, encoding='iso-8859-1')

    # Use ww getGBIFcode function to get the gbif_id for each species 
    #(name column) and save the result in a new column
    df['gbif_id'] = df.apply(lambda x: functions.getGBIFcode(x['name']),axis=1)

    def add_species(x,y):
        """
        Adds a species to the taxa_concepts table in the parameters database.

        Arguments:
        x -- species scientific name.
        y -- species gbif id.
        """
        
        stmt = """INSERT INTO taxa_concepts (taxon_id, gbif_id, scientific_name)
                  VALUES ("{0}", {1}, "{0}");""".format(x, y)
        print(stmt)
        cursor.execute(stmt)
        return True
        
    # Add each species' info to the parameters database
    result = [add_species(x,y) for x, y in zip(df['name'],df['gbif_id'])]

    conn.commit()  
    
    df.to_csv(species_file, encoding='iso-8859-1')

if __name__ == "__main__":
    main()

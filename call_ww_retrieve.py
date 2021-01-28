import wranglerconfig as config
import wrangler_functions as functions
import sqlite3
import pandas as pd

def get_primary_key_name(conn, table_name):
    """
    Returns the name of the primary key column for the table_name in the DB
    pointed to by the cursor passed in 

    Arguments:
    conn -- a sqlite DB connection object.
    table_name -- table_name to get the primary key for
    
    Notes: Uses the table_info sqlite PRAGMA statement. The PRAGMA statement
    is a SQL extension specific to SQLite that will not work with other DB engines.
    """    
    key_column = 5  # from PRAGMA table_info result set definition
    name_column = 1 # from PRAGMA table_info result set definition
    
    cursor = conn.cursor()
    get_columns = ("PRAGMA table_info('{0}')".format(table_name))
    cursor.execute(get_columns)    
    
    column_info = cursor.fetchall()
    for row in column_info:
        # a value of 1 means that column is a primary key
        if row[key_column] == 1:
            key = row[name_column]
            break
            
    # Clean up
    cursor.close()
    
    return key
    

def insert_row_as_table(db_from, table_name, row_id, db_to):
    """
    Inserts the row specified by row_id from table_name in the db_from, 
    into db_to. The resulting table has a single row with the same 
    column values as the row_id in table_name.

    Arguments:
    db_from -- database to take the row from.
    table_name -- table to copy the row from
    row_id -- row to copy
    db_to -- database to put the new table into.
    """
    import sqlite3
    import pandas as pd
        
    # Make a dataframe from the row in the from database
    conn_from = sqlite3.connect(db_from)
    # Get table_name primary key column name
    key_col = get_primary_key_name(conn_from, table_name)    
    from_df = pd.read_sql_query(sql="SELECT * FROM {0} WHERE {1} = '{2}'".format(table_name,key_col,row_id), con=conn_from)
    
    # Add the dataframe as a table in the to database
    conn_to = sqlite3.connect(db_to)
    curs_to = conn_to.cursor()    
    from_df.to_sql(name=row_id, con=conn_to, if_exists='replace')
    
    # Clean up
    curs_to.close()
    
    
def main():
    """
    - Retrieves paths, species filename and GBIF credentials from wranglerconfig.py.
    - Reads the species CSV file and uses wildlife-wrangler functions to build
      a species database for each species listed in the file.
    - Adds configuration/search parameters to the species database

    """
    
    # Specify common arguments to retrieve_gbif_occurrences
    codeDir = config.codeDir
    paramdb = config.paramdb
    gbif_req_id = 'GRINRequests'
    gbif_filter_id = 'GRINFilters'
    default_coordUncertainty = False
    outDir = config.workDir
    username = config.gbif_username
    password = config.gbif_password
    email = config.gbif_email
    speciesFilename = config.species_filename

    # Get gbif_ids of species to run from the species csv file
    df = pd.read_csv(speciesFilename, encoding='iso-8859-1')

    def build_species_db(taxon_id):
        """
        Calls the wildlife-wrangler retrieve_gbif_occurrences function
        to build a species database (spdb) for the species whose taxon_id
        is passed in.

        Arguments:
        taxon_id -- project-specific identifier and primary key for the 
        taxa_concepts table in the paramdb.
        """
        
        summary_name = taxon_id
        spdb = outDir + taxon_id + '.sqlite'
        
        # Get the occurrence data from GBIF using WW
        functions.retrieve_gbif_occurrences(codeDir, taxon_id, paramdb, spdb, gbif_req_id, gbif_filter_id, 
            default_coordUncertainty, outDir, summary_name, username, password, email)


        # Add configuration/search parameters info specific to this search   
        insert_row_as_table(paramdb, 'gbif_filters', gbif_filter_id, spdb)
        insert_row_as_table(paramdb, 'gbif_requests', gbif_req_id, spdb)
        insert_row_as_table(paramdb, 'taxa_concepts', taxon_id, spdb)
        
        
    # Iterate over df 'name' column - call build_species_db to process each species
    result = [build_species_db(x) for x in df['name']]
    
    # Build a species database for each entry in the species csv file
    for name in df:
        build_species_db(df['name'])
        
if __name__ == "__main__":
    main()







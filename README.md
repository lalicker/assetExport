# assetExport
Usage:

    --username/-u your username
  
    --passwword/-p your password
  
    --masterOrganizationId/-m your top level organization UUID
  
    [--organizationId/-o] the business group or organization you wish to filter
  
    [--output-file/-f] the file you wish to write out to
    
    [--database/-d] SQLite3 database file to write results to
    
  If you do not provide an organization with the --organizationId/-o flag, all assets will be exported
  If you provide an output file with the --output-file/-f flag, the results will be written to the file you specify with the in a CSV format with field names as headers. If you do not, the output will be written to the command line
  If you provide a database file name with the --database/-d flag, the results will be written to a SQLite3 database with the name you specify, otherwise results will not be written to a database

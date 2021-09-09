# assetExport
Usage:
  
  The primary entry point is lsAsset.py. This can be called how you ordinarily call a Python3 script, either by using python3 lsAsset.py or on \*nix-like operating systems with env, by executing ./lsAsset.py. Execution flags are listed below:

    [--username/-u] your username
  
    [--passwword/-p] your password

	[--client-id/-c] your client ID

	[--client-secret/-s] your client secret
  
    [--masterOrganizationId/-m] your top level organization UUID
  
    [--organizationId/-o] the business group or organization you wish to filter
  
    [--output-file/-f] the file you wish to write out to
    
    [--database/-d] SQLite3 database file to write results to
  
  Either username and password or client ID and client secret must be provided or the script will not be able to authenticate to your account

  If you do not provide a top level organization UUID, it will be fetched based on the credentials provided

  If you do not provide an organization with the --organizationId/-o flag, all assets for the top level organization will be exported
  
  If you provide an output file with the --output-file/-f flag, the results will be written to the file you specify with the in a CSV format with field names as headers. If you do not, the output will be written to the command line
  
  If you provide a database file name with the --database/-d flag, the results will be written to a SQLite3 database with the name you specify, otherwise results will not be written to a database

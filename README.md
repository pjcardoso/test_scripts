# test scripts

* testerscript1.py 

    description: created to set a response into simulator and send a test to teted environment. uses yaml config file to get environments addresses.

    run testerscript1.py with the project three letter code and the above filename as a parameter :
        
        python testescript1.py --project <PROJ1> --input-file project1-testfile.csv
        
    By executing "python testescript1.py -h" you can see the script usage and options.
        
        usage: testescript1.py [-h] --input-file INPUT_FILE
        optional arguments:
             -h, --help            show this help message and exit
             --input-file INPUT_FILE
                                   Input file to be used
                                   
    Note that the script will create a log file for troubleshooting if needed.
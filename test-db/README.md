# catASTrophe
Automated Bug Detection in the Database Engines SQLite3.26.0

# Project

**Objectives**:

1. Evaluates the reliability of SQLite3.26.0 by detecting crashes and logic bugs. 
2. Build our own SQL generator to produce intersting queries i.e. likely to trigger bugs (crashes OR incorrect results)



# User Guide
Description of the command lines

**Since we are using docker compose up and docker exec [...] our code is not runnable with docker run using a DockerFile. We therefore provide the following commands to properly run our code.**


## Requirements
To proceed with the scripts, please make sure you installed all the following requirements by typing this command
```
pip install -r requirements.txt
```

## Run the Tool
To run the tool, type the following command
```
python main.py
```

## Arguments
#### Number of runs
``-r`` or ``--runs`` with a numerical value.
It will launch the fuzzer for this number of iterations. Default is 100.
Example run:
```
python main.py -r 100
```
#### Gcov
Add the flag ``--gcov`` to run the code with gcov enabled.
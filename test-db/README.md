# catASTrophe
Automated Bug Detection in the Database Engines SQLite3.26.0

# Requirements
To proceed with the scripts, please make sure you installed all the following requirements by typing this command
```
pip install -r requirements.txt
```

# Project

**Objectives**:

1. Evaluates the reliability of SQLite3.26.0 by detecting crashes and logic bugs. 
2. Build our own SQL generator to produce intersting queries i.e. likely to trigger bugs (crashes OR incorrect results)

**Evaluation**:

1. Bug-finding capability
2. Characteristics of the generated SQL queries
3. Code Coverage
4. Performance

# User Guide
Description of the command lines

**We have not been able to generate a Dockerfile to run our tool**

To run the tool, type the following command
```
python main.py
```

### Arguments
#### Number of run
``-r`` or ``--runs`` with a numerical value.
It will launch the fuzzer for this number of iterations. Default is 100.
#### Versions
``-v`` or ``--versions`` with an SQL engine version
It will launch the fuzzer on the specified versions.
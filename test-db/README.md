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

To run the script type the following command
```
python3 main.py
```

### Arguments
One can add argument like ``-v`` or ``--version`` with one of the following values
```
/usr/bin/sqlite3-3.26.0
/usr/bin/sqlite3-3.39.4
```
It will only launch the tester with the selected SQL engine version, otherwise it will test both by default.
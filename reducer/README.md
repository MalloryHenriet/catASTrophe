# catASTrophe
Automated Reduction of Bug-Triggering SQL Queries

# Requirements
To proceed with the scripts, please make sure you installed all the following requirements by typing this command
```
pip install -r requirements.txt
```

# Project

## Functionality
1. The reducer iteratively tries to minimze the given query by performing various updates
2. The reducer invokes a test script
3. The test script executes the minimzed query and determines whether it still triggers a bug or not
4. The script return an exit code:
    * Exit code ``0``: the bug still occurs, valid reduction
    * Exit code ``1``: the bug no longer occurs, modification should be reverted


## Evaluation

1. Quality of reduction
2. Speed of reduction

# User Guide
Description of the command lines

To run the script type the following command
```
./reducer --query <query-to-minimize> --test <test-script>
```

### Arguments
* ``--query`` is the SQL query to reduce
* ``--test`` is an arbitrary shell script that checks whether the minimzed query still triggers the bug or not

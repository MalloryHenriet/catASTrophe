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

First build the docker from the Dockerfile :
```
docker build -t reducer .
```

Then run the docker mounting your files :
```
docker run -it \
  -v "$PWD/queries-to-minimize:/reducer/queries-to-minimize" \
  -v "$PWD/test_script.sh:/reducer/test_script.sh" \
  reducer \
```

To run the script type the following command
```
./reducer --query <query-to-minimize> --test <test-script>
```

e.g.
```
./reducer --query queries-to-minimize/query6 --test test_script.sh
```

### Arguments
* ``--query`` is the SQL query to reduce
* ``--test`` is an arbitrary shell script that checks whether the minimzed query still triggers the bug or not
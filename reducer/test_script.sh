#!/bin/bash

QUERY_FILE="${TEST_CASE_LOCATION:-minimized.sql}"
ORACLE_FILE="$(dirname "$QUERY_FILE")/oracle.txt"

# Ensure oracle.txt exists
if [ ! -f "$ORACLE_FILE" ]; then
  echo "Missing oracle.txt for: $QUERY_FILE"
  exit 1
fi

ORACLE=$(head -n 1 "$ORACLE_FILE")

# Handle CRASH(version)
if [[ "$ORACLE" =~ ^CRASH\\((.*)\\)$ ]]; then
  VERSION=${BASH_REMATCH[1]}
  /usr/bin/sqlite3-"$VERSION" < "$QUERY_FILE" > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    exit 0  # crash still happens
  else
    exit 1  # crash disappeared
  fi
fi

# Handle DIFF
if [[ "$ORACLE" == "DIFF" ]]; then
  OUTPUT1=$(/usr/bin/sqlite3-3.26.0 < "$QUERY_FILE" 2>&1)
  OUTPUT2=$(/usr/bin/sqlite3-3.39.4 < "$QUERY_FILE" 2>&1)
  [ "$OUTPUT1" != "$OUTPUT2" ] && exit 0 || exit 1
fi


echo "Unknown oracle: $ORACLE"

exit 1
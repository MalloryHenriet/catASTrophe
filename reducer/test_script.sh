#!/bin/bash

# Check if TEST_CASE_LOCATION is set
if [ -z "$TEST_CASE_LOCATION" ]; then
  echo "TEST_CASE_LOCATION is not set"
  exit 1
fi

QUERY_FILE="$TEST_CASE_LOCATION"
ORACLE_FILE="$(dirname "$QUERY_FILE")/oracle.txt"

# Ensure oracle.txt exists
if [ ! -f "$ORACLE_FILE" ]; then
  echo "Missing oracle.txt for: $QUERY_FILE"
  exit 1
fi

ORACLE=$(head -n 1 "$ORACLE_FILE")

# Handle CRASH(version)
if [[ "$ORACLE" =~ ^CRASH\((.*)\)$ ]]; then
  VERSION="${BASH_REMATCH[1]}"
  SQLITE_BIN="/usr/bin/sqlite3-$VERSION"

  if [ ! -x "$SQLITE_BIN" ]; then
    echo "SQLite version $VERSION not found at $SQLITE_BIN"
    exit 1
  fi

  # Run SQLite under timeout and capture signal-based failures
  timeout 3s "$SQLITE_BIN" < "$QUERY_FILE" > /dev/null 2>sqlite_error.log
  EXIT_CODE=$?

  # If killed by signal (128 + N), it's a crash
  if [ $EXIT_CODE -ge 128 ]; then
    rm -f sqlite_error.log
    exit 0  # valid crash
  fi

  # Filter typical SQL errors
  if grep -qi "error:" sqlite_error.log; then
    rm -f sqlite_error.log
    exit 1  # not a crash
  fi

  # Not a crash
  rm -f sqlite_error.log
  exit 1
fi

# Handle DIFF
if [[ "$ORACLE" == "DIFF" ]]; then
  OUTPUT1=$(/usr/bin/sqlite3-3.26.0 < "$QUERY_FILE" 2>stderr1.txt)
  STDERR1=$(<stderr1.txt)

  OUTPUT2=$(/usr/bin/sqlite3-3.39.4 < "$QUERY_FILE" 2>stderr2.txt)
  STDERR2=$(<stderr2.txt)

  rm -f stderr1.txt stderr2.txt

  # Check if either crashes
  STATUS1=$(/usr/bin/sqlite3-3.26.0 < "$QUERY_FILE" > /dev/null 2>&1; echo $?)
  STATUS2=$(/usr/bin/sqlite3-3.39.4 < "$QUERY_FILE" > /dev/null 2>&1; echo $?)

  if [[ $STATUS1 -ne 0 && $STATUS2 -ne 0 ]]; then
    exit 1  # both errored: invalid
  fi

  # If one failed and the other didn't: valid diff
  if [[ $STATUS1 -ne $STATUS2 ]]; then
    exit 0
  fi

  # Compare stdout or stderr
  if [[ "$OUTPUT1" != "$OUTPUT2" || "$STDERR1" != "$STDERR2" ]]; then
    exit 0  # observed difference
  else
    exit 1  # same behavior
  fi
fi

echo "Unknown oracle: $ORACLE"

exit 1
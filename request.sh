#!/usr/bin/env bash
# Sends `POST` request to Flask application `qaws_app`.

if [[ ${1} ]]
then
    curl -X POST http://127.0.0.1:8000/ \
        -H 'Content-Type: application/json' \
        -d '{"questions_num":'${1}'}'
    printf "\n"
else
    printf "Input not negative integer (number of questions).\n"
    printf "    Example: ./request.sh 1 \n"
fi

#!/bin/bash

endpoint="https://309fcajnr1.execute-api.ap-northeast-1.amazonaws.com/dev"

curl -v $endpoint/images/presigned-url?format=png | jq

#!/bin/bash

endpoint="https://309fcajnr1.execute-api.ap-northeast-1.amazonaws.com/dev"

presigned_url=$(curl -s "$endpoint/images/presigned-url?format=png" | jq -r '.uploadUrl')

if [ -z "$presigned_url" ]; then
  echo "Error: Failed to get presigned URL."
  exit 1
fi

curl -v -X PUT \
  -H "Content-Type: image/png" \
  --data-binary "@sam.png" \
  "$presigned_url"

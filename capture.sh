#!/bin/bash

URL=$(node get_stream.js $1)

ffmpeg -protocol_whitelist "file,http,https,tcp,tls" -i $URL -c copy $1.mkv

#!/data/data/com.termux/files/usr/bin/bash

if [ ! -d ./mltd ]; then
    mkdir mltd
    pkg ins jq
fi
ARCHITECTURE=`dpkg --print-architecture`
URL=`curl -s 'https://api.github.com/repos/RainbowUnicorn7297/mltd-relive/releases?per_page=3' | jq -r '[.[] | select(.tag_name | startswith("standalone"))][0] | .assets[] | select(.name | contains("'"$ARCHITECTURE"'")).browser_download_url'`
curl "$URL" -o mltd/run -L
chmod +x mltd/run
if [ ! -f ./mltd/config.ini ]; then
    LANGUAGE=
    while [ "$LANGUAGE" != zh ] && [ "$LANGUAGE" != ko ]; do
        read -p "Enter game client language: [zh/ko] " LANGUAGE
    done
    cd mltd
    ./run -c -l "$LANGUAGE"
fi

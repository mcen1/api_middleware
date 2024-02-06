apk --no-cache add coreutils python3 py3-pip curl busybox-extras jq && \
apk --no-cache add --virtual build-dependencies build-base python3-dev && \
pip3 install --upgrade  --break-system-packages pip && \
pip3 install  --break-system-packages -r requirements.txt && \
apk add git && \
apk del build-dependencies


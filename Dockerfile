FROM alpine:latest

RUN mkdir -p /usr/team

WORKDIR /usr/team

COPY ./src/ /usr/team/
COPY ./requirements.txt /usr/team/requirements.txt
COPY main.yml /usr/team/main.yml
COPY automation_endpoint_config.yml /usr/team/automation_endpoint_config.yml
COPY ./templates/ /usr/team/templates/
COPY ./ssl/ca-cert.pem /usr/local/share/ca-certificates/my-cert.crt
COPY openssl.cnf /etc/openssl.cnf
ENV OPENSSL_CONF=/etc/openssl.cnf


RUN cat /usr/local/share/ca-certificates/my-cert.crt >> /etc/ssl/certs/ca-certificates.crt && \
    apk --no-cache add coreutils python3 py3-pip curl busybox-extras jq && \
    apk --no-cache add --virtual build-dependencies build-base python3-dev && \
    pip3 install --upgrade  --break-system-packages pip && \
    pip3 install  --break-system-packages -r requirements.txt && \
    apk add git && \
    apk del build-dependencies && \
    addgroup -S notroot && \
    adduser -S notroot -G notroot && \
    chown -R notroot:notroot /usr/team/ && \
    ls -la && \
#    ansible-playbook main.yml && \
    ls -la /usr/team/routers/v1/automation/


WORKDIR /usr/team/

EXPOSE 8000

USER notroot

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--root-path", "/teampi"]

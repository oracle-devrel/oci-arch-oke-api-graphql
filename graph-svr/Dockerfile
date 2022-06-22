# Copyright(c) 2022, Oracle and / or its affiliates.
# All rights reserved. The Universal Permissive License(UPL), Version 1.0 as shown at http: // oss.oracle.com/licenses/upl
FROM oraclelinux:8
WORKDIR /app
EXPOSE 80
RUN dnf -y module enable nodejs:16 && \
  dnf -y install nodejs npm && \
  rm -rf /var/cache/dnf
ADD *.json ./
RUN npm install
HEALTHCHECK --start-period=60s --timeout=60s CMD curl -f localhost:80/graphql?query=%7B__typename%7D || exit 1
ADD *.cfg *.js *.graphql probe.sh ./
ENTRYPOINT ["/bin/npm", "start"]
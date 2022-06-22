# Copyright(c) 2022, Oracle and / or its affiliates.
# All rights reserved. The Universal Permissive License(UPL), Version 1.0 as shown at http: // oss.oracle.com/licenses/upl
FROM oraclelinux:8-slim
WORKDIR /app
RUN microdnf install python38 python38-libs python38-pip python38-setuptools
RUN update-alternatives --set python3 /usr/bin/python3.8
RUN python3 -m pip install Flask
ADD *.py *.json *.cfg ./
EXPOSE 8080
HEALTHCHECK --start-period=60s --timeout=30s CMD curl -f localhost:8080/health || exit 1
ENTRYPOINT ["python3", "events-svc.py"]
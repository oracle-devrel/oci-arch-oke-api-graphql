#!/bin/sh
# this is differs from the dos approach as running on a mac we need to use the docker buildx feature to build for amd64 rather than arm64
# docker build -t event-data-svc:latest .  # this is for a local build
# Paramters are:
# $1 is the username 
# $2 is the token/password
# $3 is the Tenancy name  we.g. myTenancy
# $4 is the OCI Region in short form e.g. iad

name=graphql-svr-svc

echo "deploying for  $1"
docker login -u ${3}/identitycloudservice/${1} -p $2  ${4}.ocir.io
docker buildx build --platform linux/amd64 --push -t ${4}.ocir.io/ociobenablement/${name}:latest .
#docker logout ${4}.ocir.io/${3}/
kubectl delete deployment ${name}-deploy
sleep 15
kubectl apply -f ./deployment.yaml
kubectl apply -f ./${name}.yaml
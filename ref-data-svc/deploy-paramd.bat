rem build the docker image and set the tag
# %1 is the username 
# %2 is the token/password
# %3 is the Tenancy name
# %4 is the OCI Region in short form e.g. iad

set name=ref-data-svc
set podname=ref-data-pod

echo deploying %name% for %1
echo 

docker build -t %name% .
docker tag %name%:latest %4.ocir.io/%3/%name%:latest

rem acces OCIR and upload the container
docker login -u %3/identitycloudservice/%1 -p %2  %4.ocir.io
docker push %4.ocir.io/%3/%name%:latest

rem deploy the container and then the service wrapper
kubectl apply -f ./deployment.yaml
kubectl apply -f ./%name%.yaml

kubectl delete pod -l app=%podname%
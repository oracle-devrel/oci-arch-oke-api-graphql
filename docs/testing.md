# Testing

With the deployment complete it is possible to prove the services.  To run the tests you will need to know:

- Your API Gateway public IP
- Your External-IP for the Kubernetes cluster if you wish to invoke the services directly.

You may wish to apply the following steps using a tool like [Postman](https://www.postman.com/) as it simplified the task

### Calling Resolvers Directly

There are several approaches by which we can validate the resolvers are working well. The two we would suggest considering:

1. Install Lens - https://k8slens.dev/

   Lens app can work with the local kubectl config file to connect to a Kubernetes cluster. Having established the connection to perform the service deployment opening the connection is very easy. With the following steps:

   - Open the Kubernetes cluster shown in the list of options. This can be done by double clicking on the appropriate cluster entry.
   - In the cluster view (recognizable by the name of the cluster in the top left) expand the *Workloads* part of the left-hand navigation tree and select *Pods*. Select the Pod you want to test, this will result in a panel being displayed with the pod's details. Take note of the Pod IP and Container Port.
   - Select a different pod. The panel will update with the details of the pod. Across the panel header are icons - select the Pod shell icon (tool tips will confirm the icon to use). This will open a Terminal window. we can now use curl to perform the test.
   -  we can issue the shell to issue the command`curl -f` `<ClusterIP>:<port>/test/`  or `curl -f <ClusterIP>:<port>/health/` for testing the resolvers provided and both URIs will yield a simple response.

2. Using the kubectl command line.

   - We need to see a list of the pods currently running, using the command `kubectl get pods -o wide`
   - Using a pod other than the one we want to test (the pods can be recognized with the first part of the name we need to take note of the full pod name and the Cluster IP of the pod instance we want to test in the list of pods. The port number being used will also need to be noted - this will be one of 80, 8080, and 8090 depending upon which pod we want to interact with.
   - As the pods have a Linux base we can use a bash shell within the pod using the command `kubectl exec -it <pod name> -- /bin/bash`. This will give us a bash shell prompt that is running within the pod.
   - Having a bash shell we can issue the command `curl -f` `<ClusterIP>:<port>/test/`  or `curl -f <ClusterIP>:<port>/health/` for testing the resolvers provided and both URIs will yield a simple response.

Note: This only works because we have not applied strong security settings to the services.

### Invoking the GraphQL Server

We can test the GraphQL server both internally and externally. This can be done by executing the command curl -f `https:://ServerIP/graphql?query=%7B__typename%7D` with the ServerIP being the CLUSTER-IP or EXTERNAL-IP depending on whether you're exercising the command within the cluster as illustrated for the resolvers, or externally.

To help exercise the GraphQL server as this is the public API service we have provided a [Postman](https://www.postman.com/) Collection that can be used. is in the Test folder of the repository. Note before executing any of the invocations the following actions will be need to be done:

- server IP will need to be amended to reflect your local deployment.
- set the value for the auth-token so the call will be tolerated by the API Gateway

Each of the calls is annotated within the Postman Collection.



### Test Data

The data provided comes in two sizes. Each is backend service has its own data deployed in the container. The service's *.cfg* file (e.g. *event-svc.cfg*) dictates which data file to use. So we could easily override with a ConfigMap to add newer and bigger data sets.

Each service has a small data set and a larger data set. For example in the event-svc these are named *events-small.json* and *events.json*
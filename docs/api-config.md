## API Gateway Configuration



We want to create several simple Deployments into the API Gate. Each of the following sections describes the API and the deployment parameters

Where URLS are required these need to be URLs of the Kubernetes entry points. These can be set by copying the **Kubernetes API Private Endpoint** to the OKE configuration and appending the service name to the end, so you should have something like:

***10.0.0.131:6443***/graphql-svc



##### Directly Calling Resolvers

For test Routes 2 and 3 to work it will be necessary to create an ingress point for the services ref-data-svc and event-data-svc. This can be done utilizing the prepared Kubernetes yaml file called ref-data-ingress.yaml and event-data-ingress.yaml respectively. This can then be applied with the command *kubectl apply -f ./ref-data-ingress.yaml* which will expose the REST endpoints (without any load balancing). To remove these endpoints as we would in a production-like setup we can use the command *kubectl remove ingress ref-data-ingress* (and event-data-ingress for the corresponding ingress point).

Note: We assume you have deployed the main graphql-svr as this sets up the ingress controller that will be needed.

## Test API Deployment

This will allow us to validate that we can invoke the API Gateway properly and will return a result through the correct path. Once everything is deployed correctly this can be deleted. Within the test group, we will include direct paths to our resolvers for the purposes of testing and changes.

##### Basic Information

| Attribute   | Value |
| ----------- | ----- |
| Name        | Test  |
| Path prefix | /test |
|             |       |

##### API Request policies

| Attribute                                     | Value               |
| --------------------------------------------- | ------------------- |
| Mutual-TLS                                    | -- no values set -- |
| Authentication                                | -- no values set -- |
| CORS                                          | -- no values set -- |
| Rate limiting                                 |                     |
| Rate limiting - Number of requests per second | 1                   |
| Rate limiting - Type of rate limit            | Total               |
| Usage plans                                   | -- no values set -- |

##### API logging policies

| Attribute           | Value       |
| ------------------- | ----------- |
| Execution log level | information |

#### Route 1

| Attribute    | Value                  |
| ------------ | ---------------------- |
| Path         | /test                  |
| Methods      | GET                    |
| Type         | Stock response         |
| Status code  | 200                    |
| Body         | {"test":"response ok"} |
| Header name  | -- no value set--      |
| Header value | -- no value set --     |

#### Routes for API Gateway Protected Resolver endpoints

If you wish to expose the Resolver APIs so that the gateway can be used to enable endpoint testing then the following routes will be needed. The Kubernetes will need to be exposed by running the `expose.bat` or `expose.sh` scripts in the relevant folders.

The URL to be obtained will be the *EXTERNAL-IP* value from running the command `kubectl get services`. Then take the EXTERNAL IP related to the service wanted.  e.g. http://129.80.54.21

#### Route 2

| Attribute                                   | Value              |
| ------------------------------------------- | ------------------ |
| Path                                        | /events            |
| Methods                                     | GET, POST, DELETE  |
| Type                                        | HTTP               |
| URL                                         | xxxx               |
| Body                                        | xxx                |
| Connection establishment timeout in seconds | -- no value set--  |
| Reading response timeout in seconds         | -- no value set -- |
| Disable SSL verification                    | set                |

#### Route 3

| Attribute                                   | Value                  |
| ------------------------------------------- | ---------------------- |
| Path                                        | /refdata               |
| Methods                                     | GET, POST, DELETE      |
| Type                                        | HTTP                   |
| URL                                         | xxxx                   |
| Body                                        | {"test":"response ok"} |
| Connection establishment timeout in seconds | -- no value set--      |
| Reading response timeout in seconds         | -- no value set --     |
| Disable SSL verification                    | set                    |



## GraphQL API Deployment

This endpoint will direct the traffic to our GraphQL server.  We will prefix the path for our implemented services as /svc so our services would be /svc/data.

The URL for the GraphQL endpoint to be obtained will be the *EXTERNAL-IP* value from running the command `kubectl get services`. Then take the EXTERNAL IP related the service *lb-graphql-svc*  e.g. http://129.80.54.21



##### Basic Information

| Attribute   | Value          |
| ----------- | -------------- |
| Name        | GraphQL Server |
| Path prefix | /svc           |
|             |                |

##### API Request policies

| Attribute                                             | Value               |
| ----------------------------------------------------- | ------------------- |
| Mutual-TLS                                            | -- no values set -- |
| Authentication                                        | -- no value set --  |
| Header validations                                    |                     |
| Header validations - Add body validation - Required   | Set                 |
| Header validations - Add body validation - Media type | application/json    |
| CORS                                                  | -- no values set -- |
| Rate limiting                                         |                     |
| Rate limiting - Number of requests per second         | 1                   |
| Rate limiting - Type of rate limit                    | Total               |
| Usage plans                                           | -- no values set -- |

##### API logging policies

| Attribute           | Value       |
| ------------------- | ----------- |
| Execution log level | information |

#### Route 1

| Attribute                                   | Value              |
| ------------------------------------------- | ------------------ |
| Path                                        | /graphql           |
| Methods                                     | POST               |
| Type                                        | HTTP               |
| URL                                         | svc                |
| Body                                        |                    |
| Connection establishment timeout in seconds | -- no value set--  |
| Reading response timeout in seconds         | -- no value set -- |
| Disable SSL verification                    | set                |



### Authentication 

Once everything is running we would recommend that an authentication policy be added. The documentation to set this up is available [here](https://docs.oracle.com/en-us/iaas/Content/APIGateway/Tasks/apigatewayaddingauthzauthn.htm).

// Copyright(c) 2022, Oracle and / or its affiliates.
// All rights reserved. The Universal Permissive License(UPL), Version 1.0 as shown at http: // oss.oracle.com/licenses/upl

import { loadFilesSync } from '@graphql-tools/load-files';
import EventsInternalAPI from './EventsInternalAPI.js';
import ProviderInternalAPI from './ProviderInternalAPI.js';
import { resolvers } from './resolvers.js';
import { ApolloServer } from 'apollo-server';


const server = new ApolloServer({
  debug : false,
  typeDefs: loadFilesSync('./schema.graphql'),
  resolvers,
  dataSources: () => {
    return {
      eventsInternalAPI: new EventsInternalAPI(),
      providerInternalAPI: new ProviderInternalAPI()
    };
  }});

// The `listen` method launches a web server.
server.listen({ port: 80,}).then(({ url }) => {
  console.log(`Server ready at ${url}`);
});
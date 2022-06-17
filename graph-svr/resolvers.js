// Copyright(c) 2022, Oracle and / or its affiliates.
// All rights reserved. The Universal Permissive License(UPL), Version 1.0 as shown at http: // oss.oracle.com/licenses/upl
// useful link https://www.apollographql.com/tutorials/lift-off-part2/the-shape-of-a-resolver

import { useLogger } from "@graphql-yoga/node";

// if you don't want the service writing any logs - set this  to false
const log = true;


export const resolvers = {
  Query: {
    // if there are issues with the resolvers use this to test server config is ok
    help() {
      return "help me";
    },

    // query the event using the event id
    event: async (_parent, { id }, { dataSources }, _info)  => {
      if (log) {
        console.log("resolvers - Query event id");
      }
      let responseValue = await dataSources.eventsInternalAPI.getEvent(id);
      if (log) { console.log(`resolved event as: ${responseValue}`); }
      return responseValue;
    },

    // retrieve the latest event - no params needed
    latestEvent: async (_parent, _args, { dataSources }, _info) => {
      if (log) { console.log("resolvers - get latest event"); }
      let responseValue = await dataSources.eventsInternalAPI.getLatestEvent();
      if (log) { console.log(`Resolver response for latest event:\n ${responseValue}`); }
      return responseValue;
    },

    // get events that satisfy one or more of the parameter criteria provided
    events: async (_parent, { tsunami, alert, status, eventType, minTime, maxTime, minMag, maxMag, nameContains }, { dataSources }, _info) => {
      if (log) { console.log("Query events - tsunami=%s, alert=%s, status=%s, eventType=%s, minTime=%s, maxTime=%s, minMag=%s, maxMag=%s, nameContains=%s", tsunami, alert, status, eventType, minTime, maxTime, minMag, maxMag, nameContains); }
      let responseValue = dataSources.eventsInternalAPI.getEvents(tsunami, alert, status, eventType, minTime, maxTime, minMag, maxMag, nameContains);
      if (log) { console.log(`Get events returned: \n ${responseValue}`); }
      return responseValue;
    },

    // get a provider based on their code (unique id)
    provider: async (_parent, { code }, { dataSources }, _info) => {
      if (log) { console.log("resolvers - get provider %s", code); }
      let responseValue = await dataSources.providerInternalAPI.getProvider(code);
      if (log) { console.log(`Get provider returned: \n ${responseValue}`); }

      return responseValue;
    },

    // find provide that matches one of the supplied parameters
    findProvider: async (_parent, {code, alias, name}, { dataSources }, _info) => {
      if (log) { console.log(`resolvers get providers using ${code}, ${alias}, ${name}`); }
      let responseValue = await dataSources.providerInternalAPI.findProvider(code, alias, name);
      if (log) { console.log(`Get providers returned: \n ${responseValue}`); }

      return responseValue;      
    },
 },
  
  Mutation: {
    // supply an event structure with modifications. The respnse will be the value with ids id
    changeEvent: async (_parent, { event }, { dataSources }, _info) => {
    if (log) { console.log("mutator Change event to %s", event); }
    let responseValue = await dataSources.eventsInternalAPI.changeEvent(event);
    return responseValue;
    },

    // delete an event based on its id
    deleteEvent: async (_parent, { id }, { dataSources }, _info) => {
      if (log) { console.log("mutator Change event to %s", id); }
      let responseValue = await dataSources.eventsInternalAPI.deleteEvent(id);
      return responseValue;
    },

    // delete a provider based on the code (unique id)
    deleteProvider: async (_parent, { code }, { dataSources }, _info) => {
      if (log) { console.log("mutator remove provider %s", code); }
      let responseValue = await dataSources.providerInternalAPI.deleteProvider(code);
      return responseValue;
      }
  },

  Event: {
    // support a nested lookup so if we query an event we can also retrieve provider associated details
    providers: (event, args, { dataSources }, info) => {
      if (log) { console.log(`going to locate ${event.sources}`) }
      let responseValue = dataSources.providerInternalAPI.getProviders(event.sources);
      return responseValue;
    }
}
};


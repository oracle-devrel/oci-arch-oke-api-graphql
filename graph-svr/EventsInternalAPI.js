// Copyright(c) 2022, Oracle and / or its affiliates.
// All rights reserved. The Universal Permissive License(UPL), Version 1.0 as shown at http: // oss.oracle.com/licenses/upl
// Useful links - https://www.apollographql.com/docs/apollo-server/api/plugin/drain-http-server

import { RESTDataSource } from 'apollo-datasource-rest';
import fs from 'fs';

export default class EventsInternalAPI extends RESTDataSource {
  constructor() {
    super();
    let config = JSON.parse(fs.readFileSync('./config.json'));
    this.baseURL = 'http://' + config['event-svc-base']+'/';
    // console.log("Events REST Data Source:" + this.baseURL);
    console.log(`Events REST Data Source: ${ this.baseURL }`);
  }

  // GET
  async getEvent(id) {
    console.log("getEvent (%s) directing to %s",id,this.baseURL);
    return this.get(`event?id=${id}`);
  }

  // GET
  async getLatestEvent() {
    console.log("getLatestEvent directing to %s",this.baseURL);
    return this.get(`latestEvent`);
  }

  // build up the params part of the url prefixing as appropriate
  addParam(params, name, value)
  {
    if (params == '')
    {
      params = params + '?';
    }
    else
    {
      params = `${params}&`;
    }
  
    params = `${params}${name}=${value}`;
    return params;
  }

  // GET
  async getEvents(tsunami, alert, status, eventType, minTime, maxTime, minMag, maxMag, nameContains) {
    let params = '';
    if (tsunami != null) { params = addParam(params, 'tsunami', tsunami);}
    if (alert != null) { params = addParam(params, 'alert', alert); }
    if (status != null) { params = addParam(params, 'status', status); }
    if (eventType != null) { params = addParam(params, 'eventType', eventType); }
    if (minTime != null) { params = addParam(params, 'minTime', minTime); }
    if (maxTime != null) { params = addParam(params, 'maxTime', maxTime); }
    if (minMag != null) {params = addParam(params, 'minMag', minMag); }
    if (maxMag != null) { params = addParam(params, 'maxMag', maxMag); }
    if (nameContains != null) { params = addParam(params, 'nameContains', nameContains); }
    console.log(`GetEvents called - params being used ${params}`);
    return this.get(`events${params}`);
  }

  // POST
  async changeEvent(event) {
    return this.post(
      `event`, // path
      event // request body
    );
  }

  // DELETE
  async deleteEvent(id) {
    return this.delete(`event?id=${id}`);
  }

}
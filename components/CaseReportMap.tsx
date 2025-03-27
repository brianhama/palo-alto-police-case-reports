'use client';

import { useState, useEffect } from 'react';
import { APIProvider, Map } from '@vis.gl/react-google-maps';
import { ArrestReport } from './ArrestReport';
import { ClusteredArrestMarkers } from './ClusteredArrestMarker';

export default function CaseReportMap({reports, setSelectedReportId}: {reports: ArrestReport[], setSelectedReportId: (reportId: string) => void}) {
    
    return (
<div className="w-full h-[500px]">
<APIProvider
    apiKey="AIzaSyCmqCO1Okpep12h-jXmTeswa0kSpsIbwco">
    <Map
    mapId="4712fd750ea17be4"
      defaultZoom={13}
      gestureHandling={'greedy'}
      disableDefaultUI={true}
      defaultCenter={{ lat: 37.4419, lng: -122.1430 }}><ClusteredArrestMarkers arrests={reports} setSelectedReportId={setSelectedReportId} /></Map>
  </APIProvider></div>
    );
}

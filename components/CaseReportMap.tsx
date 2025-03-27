'use client';

import { useState, useEffect } from 'react';
import { APIProvider, Map } from '@vis.gl/react-google-maps';
import { ArrestReport } from './ArrestReport';
import { ClusteredArrestMarkers } from './ClusteredArrestMarker';

export default function CaseReportMap({reports, setSelectedReportId}: {reports: ArrestReport[], setSelectedReportId: (reportId: string) => void}) {
    
    return (
<div className="w-full h-[500px]">
<APIProvider

    apiKey="AIzaSyCYiYnOGLCOBnH0BChhpejO6_-xl3XXGlg">
    <Map
    mapId="5d57acc604008d03"
      defaultZoom={13}
      gestureHandling={'greedy'}
      disableDefaultUI={true}
      defaultCenter={{ lat: 37.4419, lng: -122.1430 }}><ClusteredArrestMarkers arrests={reports} setSelectedReportId={setSelectedReportId} /></Map>
  </APIProvider></div>
    );
}

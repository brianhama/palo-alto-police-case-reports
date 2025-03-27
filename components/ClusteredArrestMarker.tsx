'use client';

import { InfoWindow, useMap } from '@vis.gl/react-google-maps';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { type Marker, MarkerClusterer } from '@googlemaps/markerclusterer';
import { ArrestReport } from './ArrestReport';
import { ArrestMarker } from './ArrestMarker';

export type ClusteredArrestMarkersProps = {
  arrests: ArrestReport[];
  setSelectedReportId: (reportId: string) => void;
};

/**
 * The ClusteredArrestMarkers component is responsible for integrating the
 * markers with the markerclusterer.
 */
export const ClusteredArrestMarkers = ({ arrests, setSelectedReportId }: ClusteredArrestMarkersProps) => {
  const [markers, setMarkers] = useState<{ [key: string]: Marker }>({});

  const map = useMap();
  const clusterer = useMemo(() => {
    if (!map) return null;
    return new MarkerClusterer({ map });
  }, [map]);

  useEffect(() => {
    if (!clusterer) return;
    clusterer.clearMarkers();
    clusterer.addMarkers(Object.values(markers));
  }, [clusterer, markers]);

  const setMarkerRef = useCallback((marker: Marker | null, key: string) => {
    setMarkers(prevMarkers => {
      if ((marker && prevMarkers[key]) || (!marker && !prevMarkers[key])) return prevMarkers;
      if (marker) {
        return { ...prevMarkers, [key]: marker };
      } else {
        const { [key]: _, ...newMarkers } = prevMarkers;
        return newMarkers;
      }
    });
  }, []);

  const handleMarkerClick = useCallback((arrest: ArrestReport) => {
    setSelectedReportId(arrest.id.toString());
  }, []);

  return (
    <>
      {arrests.map(arrest => (
        <ArrestMarker
          key={arrest.id.toString()}
          arrest={arrest}
          onClick={handleMarkerClick}
          setMarkerRef={setMarkerRef}
        />
      ))}
    </>
  );
};
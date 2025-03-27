'use client';

import {ArrestReport} from './ArrestReport';
import type {Marker} from '@googlemaps/markerclusterer';
import React, {useCallback} from 'react';
import {AdvancedMarker} from '@vis.gl/react-google-maps';

export type ArrestMarkerProps = {
  arrest: ArrestReport;
  onClick: (arrest: ArrestReport) => void;
  setMarkerRef: (marker: Marker | null, key: string) => void;
};

/**
 * Wrapper Component for an AdvancedMarker for a single tree.
 */
export const ArrestMarker = (props: ArrestMarkerProps) => {
  const {arrest, onClick, setMarkerRef} = props;

  const handleClick = useCallback(() => onClick(arrest), [onClick, arrest]);
  const ref = useCallback(
    (marker: google.maps.marker.AdvancedMarkerElement) =>
      setMarkerRef(marker, arrest.id.toString()),
    [setMarkerRef, arrest.id]
  );

  return (
    <AdvancedMarker position={new google.maps.LatLng(arrest.latitude, arrest.longitude)} ref={ref} onClick={handleClick}>
      <span className="marker-clustering-tree">🚓</span>
    </AdvancedMarker>
  );
};
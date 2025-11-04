import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import type { ParsedNetwork, Coordinate } from '../utils/epanetParser';
import { transformPalestinianUTMToWGS84, isPalestinianUTM } from '../utils/coordinateTransform';

interface NetworkOverlayProps {
  map: L.Map | null;
  network: ParsedNetwork | null;
}

export const NetworkOverlay: React.FC<NetworkOverlayProps> = ({ map, network }) => {
  const layersRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!map || !network) return;

    console.log('NetworkOverlay: Map and network available');
    console.log('Network coordinates count:', network.coordinates.length);
    console.log('First few coordinates:', network.coordinates.slice(0, 3));

    // Clear existing layers
    if (layersRef.current) {
      map.removeLayer(layersRef.current);
    }

    // Create new layer group
    const layerGroup = L.layerGroup().addTo(map);
    layersRef.current = layerGroup;

    // Transform coordinates to WGS 84
    const transformedCoords = network.coordinates.map(coord => {
      if (isPalestinianUTM(coord.x, coord.y)) {
        const latLng = transformPalestinianUTMToWGS84(coord.x, coord.y);
        return {
          nodeId: coord.nodeId,
          latLng: latLng,
          originalCoord: coord
        };
      }
      return null;
    }).filter(Boolean) as Array<{
      nodeId: string;
      latLng: { lat: number; lng: number };
      originalCoord: Coordinate;
    }>;

    console.log('Transformed coordinates count:', transformedCoords.length);
    console.log('First few transformed coordinates:', transformedCoords.slice(0, 3));

    if (transformedCoords.length === 0) {
      console.warn('No valid coordinates found for transformation');
      return;
    }

    // Create node markers
    transformedCoords.forEach(({ nodeId, latLng }) => {
      // Find node data
      const junction = network.junctions.find(j => j.id === nodeId);
      const reservoir = network.reservoirs.find(r => r.id === nodeId);
      const tank = network.tanks.find(t => t.id === nodeId);

      let nodeType = 'Junction';
      let nodeData: any = junction;
      let markerColor = '#007bff'; // Blue for junctions

      if (reservoir) {
        nodeType = 'Reservoir';
        nodeData = reservoir;
        markerColor = '#28a745'; // Green for reservoirs
      } else if (tank) {
        nodeType = 'Tank';
        nodeData = tank;
        markerColor = '#ffc107'; // Yellow for tanks
      }

      // Create custom marker
      const marker = L.circleMarker([latLng.lat, latLng.lng], {
        radius: 6,
        fillColor: markerColor,
        color: '#fff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8
      });

      // Create popup content
      const popupContent = `
        <div style="min-width: 200px;">
          <h4 style="margin: 0 0 8px 0; color: #333;">${nodeType}: ${nodeId}</h4>
          ${nodeData ? `
            <div style="font-size: 12px; line-height: 1.4;">
              ${nodeType === 'Junction' ? `
                <p><strong>Elevation:</strong> ${nodeData.elevation} m</p>
                <p><strong>Demand:</strong> ${nodeData.demand} L/s</p>
              ` : ''}
              ${nodeType === 'Reservoir' ? `
                <p><strong>Head:</strong> ${nodeData.head} m</p>
              ` : ''}
              ${nodeType === 'Tank' ? `
                <p><strong>Elevation:</strong> ${nodeData.elevation} m</p>
                <p><strong>Initial Level:</strong> ${nodeData.initLevel} m</p>
                <p><strong>Diameter:</strong> ${nodeData.diameter} m</p>
              ` : ''}
              <p style="margin-top: 8px; font-size: 10px; color: #666;">
                Lat: ${latLng.lat.toFixed(6)}, Lng: ${latLng.lng.toFixed(6)}
              </p>
            </div>
          ` : ''}
        </div>
      `;

      marker.bindPopup(popupContent);
      marker.addTo(layerGroup);
    });

    // Create pipe lines
    network.pipes.forEach(pipe => {
      const node1Coord = transformedCoords.find(c => c.nodeId === pipe.node1);
      const node2Coord = transformedCoords.find(c => c.nodeId === pipe.node2);

      if (node1Coord && node2Coord) {
        const line = L.polyline([
          [node1Coord.latLng.lat, node1Coord.latLng.lng],
          [node2Coord.latLng.lat, node2Coord.latLng.lng]
        ], {
          color: '#dc3545', // Red for pipes
          weight: 2,
          opacity: 0.7
        });

        // Create pipe popup
        const pipePopupContent = `
          <div style="min-width: 200px;">
            <h4 style="margin: 0 0 8px 0; color: #333;">Pipe: ${pipe.id}</h4>
            <div style="font-size: 12px; line-height: 1.4;">
              <p><strong>From:</strong> ${pipe.node1}</p>
              <p><strong>To:</strong> ${pipe.node2}</p>
              <p><strong>Length:</strong> ${pipe.length} m</p>
              <p><strong>Diameter:</strong> ${pipe.diameter} mm</p>
              <p><strong>Roughness:</strong> ${pipe.roughness}</p>
              <p><strong>Status:</strong> ${pipe.status}</p>
            </div>
          </div>
        `;

        line.bindPopup(pipePopupContent);
        line.addTo(layerGroup);
      }
    });

    // Create pump lines
    network.pumps.forEach(pump => {
      const node1Coord = transformedCoords.find(c => c.nodeId === pump.node1);
      const node2Coord = transformedCoords.find(c => c.nodeId === pump.node2);

      if (node1Coord && node2Coord) {
        const line = L.polyline([
          [node1Coord.latLng.lat, node1Coord.latLng.lng],
          [node2Coord.latLng.lat, node2Coord.latLng.lng]
        ], {
          color: '#6f42c1', // Purple for pumps
          weight: 3,
          opacity: 0.8,
          dashArray: '5, 5'
        });

        const pumpPopupContent = `
          <div style="min-width: 200px;">
            <h4 style="margin: 0 0 8px 0; color: #333;">Pump: ${pump.id}</h4>
            <div style="font-size: 12px; line-height: 1.4;">
              <p><strong>From:</strong> ${pump.node1}</p>
              <p><strong>To:</strong> ${pump.node2}</p>
              <p><strong>Parameters:</strong> ${pump.parameters}</p>
            </div>
          </div>
        `;

        line.bindPopup(pumpPopupContent);
        line.addTo(layerGroup);
      }
    });

    // Fit map to show all network elements
    if (transformedCoords.length > 0) {
      const bounds = L.latLngBounds(
        transformedCoords.map(c => [c.latLng.lat, c.latLng.lng])
      );
      map.fitBounds(bounds, { padding: [20, 20] });
    }

    // Cleanup function
    return () => {
      if (layersRef.current) {
        map.removeLayer(layersRef.current);
        layersRef.current = null;
      }
    };
  }, [map, network]);

  return null; // This component doesn't render anything visible
};

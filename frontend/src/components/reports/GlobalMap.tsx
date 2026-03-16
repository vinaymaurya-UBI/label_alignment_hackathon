import React from "react";
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix for default marker icons in Leaflet
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

interface Location {
  id: string | number;
  country_code: string;
  lat: number;
  lng: number;
  status: "approved" | "pending" | "rejected" | string;
  authority: string;
}

const COUNTRY_COORDS: Record<string, [number, number]> = {
  US: [37.0902, -95.7129],
  EU: [50.8503, 4.3517], // Brussels as center for EU
  GB: [55.3781, -3.436],
  CA: [56.1304, -106.3468],
  JP: [36.2048, 138.2529],
  AU: [-25.2744, 133.7751],
  CH: [46.8182, 8.2275],
};

const STATUS_COLORS: Record<string, string> = {
  approved: "#10b981", // emerald-500
  pending: "#f59e0b",  // amber-500
  rejected: "#ef4444", // red-500
};

const GlobalMap = ({ countries }: { countries: string[] }) => {
  const locations: Location[] = countries.map((cc, idx) => ({
    id: idx,
    country_code: cc,
    lat: COUNTRY_COORDS[cc]?.[0] || 0,
    lng: COUNTRY_COORDS[cc]?.[1] || 0,
    status: "approved", // Default for now
    authority: cc === "US" ? "FDA" : cc === "EU" ? "EMA" : "Health Authority",
  })).filter(loc => loc.lat !== 0);

  return (
    <div className="h-[400px] w-full rounded-3xl overflow-hidden border border-slate-100 shadow-sm relative z-0">
      <MapContainer 
        center={[20, 0]} 
        zoom={2} 
        scrollWheelZoom={false}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />
        {locations.map((loc) => (
          <CircleMarker
            key={loc.id}
            center={[loc.lat, loc.lng]}
            radius={8}
            pathOptions={{ 
              fillColor: STATUS_COLORS[loc.status], 
              color: "white", 
              weight: 2, 
              fillOpacity: 0.8 
            }}
          >
            <Popup className="custom-popup">
              <div className="p-1">
                <h4 className="font-bold text-slate-900">{loc.country_code} ({loc.authority})</h4>
                <p className="text-xs text-slate-500 mt-1 capitalize">Status: <span className="font-bold text-emerald-600">{loc.status}</span></p>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
};

export default GlobalMap;

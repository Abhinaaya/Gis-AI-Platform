import { useEffect, useState } from "react";
import {
  GeoJSON,
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  useMapEvents,
} from "react-leaflet";

import L from "leaflet";
import "leaflet/dist/leaflet.css";

type GeoJsonData = any;

delete (L.Icon.Default.prototype as any)._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

function LocationMarker({
  setRiskInfo,
}: {
  setRiskInfo: any;
}) {
  const [position, setPosition] =
    useState<L.LatLng | null>(null);

  const map = useMapEvents({
    async click(e) {
      const lat = e.latlng.lat;
      const lon = e.latlng.lng;

      setPosition(e.latlng);

      try {
        const response = await fetch(
          `http://127.0.0.1:8000/nearest-flood?lat=${lat}&lon=${lon}`
        );

        const data = await response.json();

        setRiskInfo(data);
      } catch (error) {
        console.error(error);
      }

      map.flyTo(e.latlng, map.getZoom());
    },
  });

  return position === null ? null : (
    <Marker position={position}>
      <Popup>You clicked here</Popup>
    </Marker>
  );
}

export default function App() {
  const [geoData, setGeoData] = useState<GeoJsonData | null>(null);

  const [floodPoints, setFloodPoints] =
    useState<any[]>([]);

  const [riskInfo, setRiskInfo] =
    useState<any>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/geo-data")
      .then((res) => res.json())
      .then((data) => setGeoData(data));

    fetch("http://127.0.0.1:8000/flood-points")
      .then((res) => res.json())
      .then((data) => setFloodPoints(data));
  }, []);

  return (
    <div
  style={{
    width: "100vw",
    height: "100vh",
  }}
>
      <MapContainer
        center={[17.385, 78.4867]}
        zoom={10}
        style={{
          height: "100%",
          width: "100%",
        }}
      >
        <TileLayer
          attribution="OpenStreetMap"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {geoData && (
          <GeoJSON
            data={geoData}
            style={{
              color: "blue",
              weight: 2,
            }}
          />
        )}

        {floodPoints.map((point, index) => (
          <Marker
            key={index}
            position={[
              point.lat,
              point.lon,
            ]}
          >
            <Popup>
              <div>
                <h3>{point.location}</h3>

                <p>
                  Risk:
                  {point.risk}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}

        <LocationMarker
          setRiskInfo={setRiskInfo}
        />
      </MapContainer>

      {riskInfo && (
        <div
          style={{
            position: "absolute",
            top: 20,
            right: 20,
            zIndex: 1000,
            background: "white",
            padding: "15px",
            borderRadius: "10px",
            boxShadow:
              "0px 0px 10px rgba(0,0,0,0.2)",
          }}
        >
          <h2>Nearest Flood Point</h2>

          <p>
            Location:
            {riskInfo.nearest_location}
          </p>

          <p>
            Risk:
            {riskInfo.risk_level}
          </p>

          <p>
            Distance:
            {riskInfo.distance_meters} meters
          </p>
        </div>
      )}
    </div>
  );
}
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

type GeoJsonData = Parameters<typeof GeoJSON>[0]["data"];

delete (L.Icon.Default.prototype as { _getIconUrl?: unknown })._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

type ClickResult = {
  lat: number;
  lon: number;
  status: string;
  region: string;
  risk: string;
  nearestFloodPoint: string;
  distance: number | null;
};

function ClickHandler({
  setClickData,
}: {
  setClickData: React.Dispatch<React.SetStateAction<ClickResult | null>>;
}) {
  useMapEvents({
    async click(e) {
      const lat = e.latlng.lat;
      const lon = e.latlng.lng;

      try {
        const [ghmcResponse, riskResponse] = await Promise.all([
          fetch(`http://127.0.0.1:8000/inside-ghmc?lat=${lat}&lon=${lon}`),
          fetch(`http://127.0.0.1:8000/analyze-risk?lat=${lat}&lon=${lon}`),
        ]);

        const ghmcData = await ghmcResponse.json();
        const riskData = await riskResponse.json();

        setClickData({
          lat,
          lon,
          status: ghmcData.status ?? "UNKNOWN",
          region: ghmcData.region_name ?? "N/A",
          risk: riskData.risk ?? "LOW",
          nearestFloodPoint: riskData.nearest_flood_point ?? "Unknown",
          distance:
            typeof riskData.distance === "number" ? riskData.distance : null,
        });
      } catch (err) {
        console.error("Fetch failed:", err);
      }
    },
  });

  return null;
}

function App() {
  const [geoData, setGeoData] = useState<GeoJsonData | null>(null);
  const [floodData, setFloodData] = useState<GeoJsonData | null>(null);
  const [clickData, setClickData] = useState<ClickResult | null>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/geo-data")
      .then((res) => res.json())
      .then((data) => {
        if (data.type === "FeatureCollection" && Array.isArray(data.features)) {
          setGeoData(data);
          return;
        }

        console.error("Invalid GHMC GeoJSON");
      })
      .catch((err) => {
        console.error("Error loading GHMC data:", err);
      });
  }, []);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/flood-data")
      .then((res) => res.json())
      .then((data) => {
        if (data.type === "FeatureCollection" && Array.isArray(data.features)) {
          setFloodData(data);
          return;
        }

        console.error("Invalid Flood GeoJSON");
      })
      .catch((err) => {
        console.error("Error loading flood data:", err);
      });
  }, []);

  return (
    <MapContainer
      center={[17.385, 78.486]}
      zoom={10}
      style={{ height: "100vh", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {geoData && (
        <GeoJSON
          data={geoData}
          style={() => ({
            color: "blue",
            fillOpacity: 0,
            weight: 4,
          })}
          onEachFeature={(feature, layer) => {
            layer.bindPopup(
              `<b>Region:</b> ${feature.properties?.name || "Unknown"}`
            );
          }}
        />
      )}

      {floodData && (
        <GeoJSON
          data={floodData}
          pointToLayer={(_, latlng) => L.marker(latlng)}
          onEachFeature={(feature, layer) => {
            layer.bindPopup(`
              <b>Flood Point</b>
              <br/><br/>
              <b>Location:</b> ${feature.properties?.Name || "Unknown"}
              <br/><br/>
              <b>Flood Risk:</b> High
            `);
          }}
        />
      )}

      <ClickHandler setClickData={setClickData} />

      {clickData && (
        <Marker position={[clickData.lat, clickData.lon]}>
          <Popup>
            <b>Latitude:</b> {clickData.lat.toFixed(5)}
            <br />
            <b>Longitude:</b> {clickData.lon.toFixed(5)}
            <br />
            <b>Status:</b> {clickData.status}
            <br />
            <b>Region:</b> {clickData.region}
            <br />
            <b>Flood Risk:</b> {clickData.risk}
            <br />
            <b>Nearest Flood Point:</b> {clickData.nearestFloodPoint}
            <br />
            <b>Distance:</b>{" "}
            {clickData.distance === null
              ? "N/A"
              : clickData.distance.toFixed(5)}
          </Popup>
        </Marker>
      )}
    </MapContainer>
  );
}

export default App;

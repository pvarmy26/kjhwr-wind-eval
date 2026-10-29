import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import './App.css';

function App() {
  const [selectedDate, setSelectedDate] = useState('2026-01-15');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async (dateStr) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/wind-analysis?date=${dateStr}`);
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(selectedDate);
  }, [selectedDate]);

  return (
    <div className="container">
      <header className="header">
        <h1>UK Wind Generation Forecast Evaluator</h1>
        <div className="date-picker">
          <label htmlFor="date">Select Date: </label>
          <input
            type="date"
            id="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
          />
        </div>
      </header>

      {loading && <div className="status">Loading evaluation metrics...</div>}
      {error && <div className="error">Failed to load data: {error}</div>}

      {data && !loading && (
        <main>
          {/* Key Metrics Dashboard */}
          <section className="metrics-grid">
            <div className="card">
              <h3>Mean Absolute Error (MAE)</h3>
              <p className="metric-value">{data.metrics.mae_mw} MW</p>
            </div>
            <div className="card">
              <h3>Root Mean Square Error (RMSE)</h3>
              <p className="metric-value">{data.metrics.rmse_mw} MW</p>
            </div>
            <div className="card">
              <h3>MAPE</h3>
              <p className="metric-value">{data.metrics.mape_percent}%</p>
            </div>
            <div className="card">
              <h3>Forecast Bias</h3>
              <p className="metric-value">{data.metrics.bias_mw} MW</p>
            </div>
            <div className={`card status-card ${data.metrics.status.toLowerCase()}`}>
              <h3>Status</h3>
              <p className="metric-value">{data.metrics.status}</p>
            </div>
          </section>

          {/* Actual vs Forecast Chart */}
          <section className="chart-section">
            <h2>Actual vs Forecast Generation (MW)</h2>
            <div style={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <LineChart data={data.series} margin={{ top: 10, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis unit=" MW" />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="actual_generation"
                    name="Actual (MW)"
                    stroke="#10b981"
                    strokeWidth={2.5}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="forecast_generation"
                    name="Forecast (MW)"
                    stroke="#3b82f6"
                    strokeWidth={2.5}
                    strokeDasharray="5 5"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </section>
        </main>
      )}
    </div>
  );
}

export default App;
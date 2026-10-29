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

export default function App() {
  const [selectedDate, setSelectedDate] = useState('2026-01-15');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAnalysis = async (date) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/wind-analysis?date=${date}`);
      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysis(selectedDate);
  }, [selectedDate]);

  return (
    <div style={{ padding: '32px', fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', backgroundColor: '#f8fafc', minHeight: '100vh', color: '#1e293b' }}>
      
      {/* Header */}
      <header style={{ marginBottom: '32px', borderBottom: '1px solid #e2e8f0', paddingBottom: '16px' }}>
        <h1 style={{ margin: 0, fontSize: '28px', color: '#0f172a' }}>UK Day-Ahead Wind Forecast Evaluation</h1>
        <p style={{ margin: '8px 0 0 0', color: '#64748b', fontSize: '15px' }}>
          Quantifying renewable generation error against Elexon actuals for Day-Ahead market decisions.
        </p>
      </header>

      {/* Date Selector */}
      <div style={{ backgroundColor: '#ffffff', padding: '16px 24px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '32px', display: 'flex', alignItems: 'center', gap: '16px' }}>
        <label htmlFor="delivery-date" style={{ fontWeight: '600', fontSize: '14px' }}>Target Delivery Date (Jan 2026):</label>
        <input
          id="delivery-date"
          type="date"
          min="2026-01-01"
          max="2026-01-31"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          style={{ padding: '8px 12px', border: '1px solid #cbd5e1', borderRadius: '6px', fontSize: '14px', outline: 'none' }}
        />
        {loading && <span style={{ fontSize: '14px', color: '#2563eb' }}>Loading latest data...</span>}
      </div>

      {error && (
        <div style={{ padding: '16px', backgroundColor: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b', borderRadius: '8px', marginBottom: '24px' }}>
          Error: {error}
        </div>
      )}

      {/* Analytics Dashboard */}
      {data && data.metrics && (
        <>
          {/* KPI Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '32px' }}>
            <div style={cardStyle}>
              <span style={cardTitleStyle}>Mean Absolute Error (MAE)</span>
              <div style={cardValueStyle}>{data.metrics.mae_mw.toLocaleString()} MW</div>
              <span style={cardSubtextStyle}>Average error magnitude</span>
            </div>

            <div style={cardStyle}>
              <span style={cardTitleStyle}>Root Mean Sq Error (RMSE)</span>
              <div style={cardValueStyle}>{data.metrics.rmse_mw.toLocaleString()} MW</div>
              <span style={cardSubtextStyle}>Penalizes large deviations</span>
            </div>

            <div style={cardStyle}>
              <span style={cardTitleStyle}>Mean Abs % Error (MAPE)</span>
              <div style={cardValueStyle}>{data.metrics.mape_percent}%</div>
              <span style={cardSubtextStyle}>Relative forecast deviation</span>
            </div>

            <div style={cardStyle}>
              <span style={cardTitleStyle}>Forecast Bias</span>
              <div style={{ ...cardValueStyle, color: data.metrics.bias_mw > 0 ? '#d97706' : '#2563eb' }}>
                {data.metrics.bias_mw > 0 ? `+${data.metrics.bias_mw}` : data.metrics.bias_mw} MW
              </div>
              <span style={{ ...cardSubtextStyle, fontWeight: '600', color: data.metrics.bias_mw > 0 ? '#d97706' : '#2563eb' }}>
                {data.metrics.status}
              </span>
            </div>
          </div>

          {/* Time-Series Plot */}
          <div style={{ backgroundColor: '#ffffff', padding: '24px', borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <h2 style={{ margin: '0 0 20px 0', fontSize: '18px', color: '#0f172a' }}>
              Actual vs. Day-Ahead Forecasted Wind Generation ({data.date})
            </h2>
            <div style={{ width: '100%', height: '420px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.series} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="time" stroke="#64748b" />
                  <YAxis stroke="#64748b" label={{ value: 'Generation (MW)', angle: -90, position: 'insideLeft', offset: 0 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }} />
                  <Legend verticalAlign="top" height={36} />
                  <Line type="monotone" dataKey="actual_generation" name="Actual Generation (MW)" stroke="#059669" strokeWidth={2.5} dot={false} />
                  <Line type="monotone" dataKey="forecast_generation" name="Day-Ahead Forecast (MW)" stroke="#2563eb" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

const cardStyle = {
  backgroundColor: '#ffffff',
  padding: '20px',
  borderRadius: '8px',
  border: '1px solid #e2e8f0',
  boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
};

const cardTitleStyle = {
  fontSize: '12px',
  color: '#64748b',
  textTransform: 'uppercase',
  fontWeight: '700',
  letterSpacing: '0.5px'
};

const cardValueStyle = {
  fontSize: '28px',
  fontWeight: '700',
  color: '#0f172a',
  margin: '8px 0 4px 0'
};

const cardSubtextStyle = {
  fontSize: '12px',
  color: '#94a3b8'
};
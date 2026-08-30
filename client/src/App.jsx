import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  TrendingUp, 
  MapPin,
  Tractor,
  Activity,
  Briefcase
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

function App() {
  const [mandis, setMandis] = useState([]);
  const [portfolio, setPortfolio] = useState({ totalValue: 0, assets: [] });
  const [loading, setLoading] = useState(true);
  const [activeCrop, setActiveCrop] = useState("Tomatoes"); 

  const priceHistory = [
    { name: 'Mon', price: 3100 },
    { name: 'Tue', price: 3150 },
    { name: 'Wed', price: 3120 },
    { name: 'Thu', price: 3200 },
    { name: 'Fri', price: 3000 },
    { name: 'Sat', price: 2900 },
    { name: 'Sun', price: 2800 },
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const portRes = await fetch('http://localhost:5000/api/portfolio');
        if (portRes.ok) {
          const pData = await portRes.json();
          setPortfolio({
            totalValue: pData.totalValue || 0,
            assets: pData.assets || []
          });
        }

        const priceRes = await fetch(`http://localhost:5000/api/prices?crop=${activeCrop}`);
        if (priceRes.ok) {
          const data = await priceRes.json();
          setMandis(data);
        }
      } catch (err) {
        console.error("Error fetching data:", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [activeCrop]);

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <Tractor size={28} color="#2563eb" />
          KisanMandi
        </div>
        <nav className="nav-links">
          <div className="nav-item active"><LayoutDashboard size={20} /> Dashboard</div>
          <div className="nav-item"><Briefcase size={20} /> My Portfolio</div>
          <div className="nav-item"><TrendingUp size={20} /> Price Trends</div>
          <div className="nav-item"><MapPin size={20} /> Routing</div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <h1>Welcome, Farmer</h1>
        <p className="subtitle">Real-time Trading & Logistics Dashboard</p>

        {/* Portfolio Section */}
        <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr', marginBottom: '32px' }}>
          <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2><Briefcase size={24} color="#2563eb" /> Agri-Stock Portfolio</h2>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Total Net Worth</div>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--text-main)' }}>₹{(portfolio.totalValue || 0).toLocaleString()}</div>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: '16px', overflowX: 'auto' }}>
              {portfolio.assets.map((asset, idx) => (
                <div key={idx} onClick={() => setActiveCrop(asset.crop)} style={{ 
                  background: activeCrop === asset.crop ? '#eff6ff' : '#f8fafc', 
                  padding: '16px', 
                  borderRadius: '8px', 
                  minWidth: '200px', 
                  cursor: 'pointer', 
                  border: activeCrop === asset.crop ? '1px solid #2563eb' : '1px solid var(--border-color)' 
                }}>
                  <div style={{ fontSize: '18px', fontWeight: '600', color: 'var(--text-main)' }}>{asset.crop}</div>
                  <div style={{ fontSize: '14px', color: 'var(--text-muted)', marginBottom: '8px' }}>{asset.quantity} Quintals</div>
                  <div style={{ fontSize: '16px', color: 'var(--accent-green)', fontWeight: '600' }}>₹{(asset.totalValue || 0).toLocaleString()}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="dashboard-grid">
          {/* Left Column (Table) */}
          <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 style={{ margin: 0 }}><Activity size={20} color="#10b981" /> Live Intelligence: {activeCrop}</h2>
            </div>
            
            {loading ? (
              <p style={{ color: 'var(--text-muted)' }}>Loading market data...</p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Mandi</th>
                    <th>Distance</th>
                    <th>True Profit (₹/q)</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {mandis.map((mandi, idx) => {
                    let badgeClass = 'hold';
                    if (mandi.recommendation.includes('100%')) badgeClass = 'sell';
                    if (mandi.recommendation.includes('50%')) badgeClass = 'sell-partial'; 
                    
                    return (
                      <tr key={idx} title={mandi.reasoning}>
                        <td style={{ fontWeight: 500 }}>{mandi.mandiName}</td>
                        <td style={{ color: 'var(--text-muted)' }}>{mandi.distanceKm} km</td>
                        <td style={{ color: 'var(--text-main)', fontWeight: 600 }}>₹{mandi.netEarning}</td>
                        <td>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', alignItems: 'flex-start' }}>
                            <span className={`badge ${badgeClass}`}>
                              {mandi.recommendation}
                            </span>
                            <span style={{ fontSize: '11px', color: 'var(--text-muted)', maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                              {mandi.reasoning}
                            </span>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>

          {/* Right Column (Chart) */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div className="glass-panel" style={{ flex: 1, minHeight: '300px' }}>
              <h2 style={{ fontSize: '16px', marginBottom: '16px' }}>{activeCrop} Market Trend</h2>
              <div style={{ width: '100%', height: '220px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={priceHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                    <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} domain={['dataMin - 100', 'dataMax + 100']} />
                    <Tooltip 
                      contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                      itemStyle={{ color: '#2563eb', fontWeight: 600 }}
                    />
                    <Line type="monotone" dataKey="price" stroke="#2563eb" strokeWidth={3} dot={{ fill: '#ffffff', r: 4, strokeWidth: 2, stroke: '#2563eb' }} activeDot={{ r: 6, fill: '#2563eb' }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

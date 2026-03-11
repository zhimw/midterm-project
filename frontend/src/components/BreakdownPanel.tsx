import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import type { Breakdown } from '@/types';

interface BreakdownPanelProps {
  breakdown: Breakdown;
  modulesUsed: string[];
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

export const BreakdownPanel: React.FC<BreakdownPanelProps> = ({ breakdown, modulesUsed }) => {
  if (!breakdown || Object.keys(breakdown).length === 0) {
    return null;
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="breakdown-panel">
      <h2>Analysis Breakdown</h2>
      
      <div className="modules-used">
        <strong>Modules Analyzed:</strong>{' '}
        {modulesUsed.map(m => m.replace('_', ' ')).join(', ')}
      </div>

      <div className="breakdown-sections">
        {breakdown.tax && (
          <div className="breakdown-section tax-section">
            <h3>Tax Optimization</h3>
            
            {breakdown.tax.strategies && breakdown.tax.strategies.length > 0 && (
              <div className="subsection">
                <h4>Recommended Strategies</h4>
                <ul>
                  {breakdown.tax.strategies.slice(0, 5).map((strategy, idx) => (
                    <li key={idx}>{strategy}</li>
                  ))}
                </ul>
              </div>
            )}

            {breakdown.tax.key_considerations && breakdown.tax.key_considerations.length > 0 && (
              <div className="subsection">
                <h4>Key Considerations</h4>
                <ul>
                  {breakdown.tax.key_considerations.map((consideration, idx) => (
                    <li key={idx}>{consideration}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {breakdown.investment && (
          <div className="breakdown-section investment-section">
            <h3>Investment Allocation</h3>
            
            <div className="subsection">
              <h4>Risk Profile: {breakdown.investment.risk_profile}</h4>
              <p className="tax-efficiency">
                Tax Efficiency Score: <strong>{breakdown.investment.tax_efficiency_score.toFixed(1)}/100</strong>
              </p>
            </div>

            {breakdown.investment.allocation && Object.keys(breakdown.investment.allocation).length > 0 && (
              <div className="subsection">
                <h4>Recommended Allocation</h4>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie
                        data={Object.entries(breakdown.investment.allocation).map(([name, value]) => ({
                          name: name.replace('_', ' '),
                          value
                        }))}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={false}
                        outerRadius={85}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {Object.keys(breakdown.investment.allocation).map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => `${value}%`} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '6px 12px', marginTop: '6px' }}>
                    {Object.entries(breakdown.investment.allocation).map(([asset], index) => (
                      <span key={asset} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: '10px', whiteSpace: 'nowrap' }}>
                        <span style={{ width: 8, height: 8, borderRadius: '50%', background: COLORS[index % COLORS.length], flexShrink: 0, display: 'inline-block' }} />
                        {asset.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="allocation-table">
                  {Object.entries(breakdown.investment.allocation).map(([asset, percentage]) => (
                    <div key={asset} className="allocation-row">
                      <span>{asset.replace('_', ' ')}</span>
                      <span className="percentage">{percentage}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {breakdown.estate && (
          <div className="breakdown-section estate-section">
            <h3>Estate Planning</h3>
            
            <div className="subsection">
              <h4>Estate Value: {formatCurrency(breakdown.estate.estate_value)}</h4>
              {breakdown.estate.estate_value > 13610000 && (
                <p className="warning">
                  ⚠️ Estate exceeds federal exemption ($13.61M) - estate tax planning critical
                </p>
              )}
            </div>

            {breakdown.estate.triggers && breakdown.estate.triggers.length > 0 && (
              <div className="subsection">
                <h4>Planning Triggers</h4>
                <ul>
                  {breakdown.estate.triggers.map((trigger, idx) => (
                    <li key={idx}>{trigger}</li>
                  ))}
                </ul>
              </div>
            )}

            {breakdown.estate.structures && breakdown.estate.structures.length > 0 && (
              <div className="subsection">
                <h4>Recommended Structures</h4>
                <div className="structures-list">
                  {breakdown.estate.structures.map((structure, idx) => (
                    <div key={idx} className="structure-item">
                      <div className="structure-type">{structure.type}</div>
                      <div className="structure-purpose">{structure.purpose}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

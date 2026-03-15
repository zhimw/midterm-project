import React, { useState } from 'react';
import type { UserProfile } from '@/types';

interface IntakeFormProps {
  onSubmit: (profile: UserProfile) => void;
}

export const IntakeForm: React.FC<IntakeFormProps> = ({ onSubmit }) => {
  const [step, setStep] = useState(1);
  const [profile, setProfile] = useState<Partial<UserProfile>>({
    age: 45,
    income: 500000,
    filing_status: 'married',
    state: 'NY',
    assets: {
      cash: 2000000,
      stocks: 1000000,
    },
    family: {},
    life_events: [],
    goals: [],
    investment_goals: [],
    estate_goals: [],
    risk_tolerance: 'moderate',
    time_horizon: 'long-term',
  });

  const updateProfile = (field: string, value: any) => {
    setProfile(prev => ({ ...prev, [field]: value }));
  };

  const updateAssets = (asset: string, value: number) => {
    setProfile(prev => ({
      ...prev,
      assets: { ...prev.assets, [asset]: value }
    }));
  };

  const updateFamily = (field: string, value: any) => {
    setProfile(prev => ({
      ...prev,
      family: { ...prev.family, [field]: value }
    }));
  };

  const toggleLifeEvent = (event: string) => {
    setProfile(prev => {
      const events = prev.life_events || [];
      const newEvents = events.includes(event)
        ? events.filter(e => e !== event)
        : [...events, event];
      return { ...prev, life_events: newEvents };
    });
  };

  const toggleGoal = (goal: string, type: 'goals' | 'investment_goals' | 'estate_goals') => {
    setProfile(prev => {
      const goals = prev[type] || [];
      const newGoals = goals.includes(goal)
        ? goals.filter(g => g !== goal)
        : [...goals, goal];
      return { ...prev, [type]: newGoals };
    });
  };

  const handleSubmit = () => {
    onSubmit(profile as UserProfile);
  };

  return (
    <div className="intake-form">
      <div className="form-header">
        <h1>Family Office Profile</h1>
        <div className="step-indicator">
          Step {step} of 4
        </div>
      </div>

      <div className="form-content">
        {step === 1 && (
          <div className="form-section">
            <h2>Basic Information</h2>
            
            <div className="form-group">
              <label>Age</label>
              <input
                type="number"
                value={profile.age}
                onChange={(e) => updateProfile('age', parseInt(e.target.value) || 0)}
                min="18"
                max="120"
              />
            </div>

            <div className="form-group">
              <label>Annual Income ($)</label>
              <input
                type="number"
                value={profile.income}
                onChange={(e) => updateProfile('income', parseFloat(e.target.value) || 0)}
                min="0"
                step="10000"
              />
            </div>

            <div className="form-group">
              <label>Filing Status</label>
              <select
                value={profile.filing_status}
                onChange={(e) => updateProfile('filing_status', e.target.value)}
              >
                <option value="single">Single</option>
                <option value="married">Married Filing Jointly</option>
                <option value="married_separate">Married Filing Separately</option>
                <option value="head_of_household">Head of Household</option>
              </select>
            </div>

            <div className="form-group">
              <label>State of Residence</label>
              <select
                value={profile.state}
                onChange={(e) => updateProfile('state', e.target.value)}
              >
                <option value="NY">New York</option>
                <option value="CA">California</option>
                <option value="FL">Florida</option>
                <option value="TX">Texas</option>
                <option value="WA">Washington</option>
                <option value="NJ">New Jersey</option>
                <option value="IL">Illinois</option>
                <option value="MA">Massachusetts</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="form-section">
            <h2>Assets & Net Worth</h2>
            
            <div className="form-group">
              <label>Cash & Cash Equivalents ($)</label>
              <input
                type="number"
                value={profile.assets?.cash || 0}
                onChange={(e) => updateAssets('cash', parseFloat(e.target.value) || 0)}
                min="0"
                step="10000"
              />
            </div>

            <div className="form-group">
              <label>Stocks & Equities ($)</label>
              <input
                type="number"
                value={profile.assets?.stocks || 0}
                onChange={(e) => updateAssets('stocks', parseFloat(e.target.value) || 0)}
                min="0"
                step="10000"
              />
            </div>

            <div className="form-group">
              <label>Bonds & Fixed Income ($)</label>
              <input
                type="number"
                value={profile.assets?.bonds || 0}
                onChange={(e) => updateAssets('bonds', parseFloat(e.target.value) || 0)}
                min="0"
                step="10000"
              />
            </div>

            <div className="form-group">
              <label>Real Estate ($)</label>
              <input
                type="number"
                value={profile.assets?.real_estate || 0}
                onChange={(e) => updateAssets('real_estate', parseFloat(e.target.value) || 0)}
                min="0"
                step="10000"
              />
            </div>

            <div className="form-group">
              <label>Business Interests ($)</label>
              <input
                type="number"
                value={profile.assets?.business || 0}
                onChange={(e) => updateAssets('business', parseFloat(e.target.value) || 0)}
                min="0"
                step="10000"
              />
            </div>

            <div className="form-group">
              <label>Other Assets ($)</label>
              <input
                type="number"
                value={profile.assets?.other || 0}
                onChange={(e) => updateAssets('other', parseFloat(e.target.value) || 0)}
                min="0"
                step="10000"
              />
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="form-section">
            <h2>Family & Life Events</h2>
            
            <div className="form-group">
              <label>Number of Children</label>
              <input
                type="number"
                value={profile.family?.children || 0}
                onChange={(e) => updateFamily('children', parseInt(e.target.value) || 0)}
                min="0"
                max="20"
              />
            </div>

            <div className="form-group">
              <label>Recent Life Events (select all that apply)</label>
              <div className="checkbox-group">
                {['marriage', 'divorce', 'widowed', 'birth', 'adoption', 'business_sale', 'inheritance', 'retirement'].map(event => (
                  <label key={event} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={profile.life_events?.includes(event)}
                      onChange={() => toggleLifeEvent(event)}
                    />
                    <span>{event.replace('_', ' ')}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="form-section">
            <h2>Goals & Risk Preferences</h2>
            
            <div className="form-group">
              <label>Financial Goals</label>
              <div className="checkbox-group">
                {['retirement planning', 'wealth preservation', 'wealth growth', 'college funding', 'business succession'].map(goal => (
                  <label key={goal} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={profile.goals?.includes(goal)}
                      onChange={() => toggleGoal(goal, 'goals')}
                    />
                    <span>{goal}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>Investment Goals</label>
              <div className="checkbox-group">
                {['tax efficiency', 'income generation', 'capital appreciation', 'ESG alignment'].map(goal => (
                  <label key={goal} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={profile.investment_goals?.includes(goal)}
                      onChange={() => toggleGoal(goal, 'investment_goals')}
                    />
                    <span>{goal}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>Estate Planning Goals</label>
              <div className="checkbox-group">
                {['minimize estate taxes', 'wealth transfer', 'asset protection', 'charitable legacy'].map(goal => (
                  <label key={goal} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={profile.estate_goals?.includes(goal)}
                      onChange={() => toggleGoal(goal, 'estate_goals')}
                    />
                    <span>{goal}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>Risk Tolerance</label>
              <select
                value={profile.risk_tolerance}
                onChange={(e) => updateProfile('risk_tolerance', e.target.value)}
              >
                <option value="conservative">Conservative</option>
                <option value="moderate">Moderate</option>
                <option value="aggressive">Aggressive</option>
              </select>
            </div>

            <div className="form-group">
              <label>Investment Time Horizon</label>
              <select
                value={profile.time_horizon}
                onChange={(e) => updateProfile('time_horizon', e.target.value)}
              >
                <option value="short-term">Short-term (&lt;3 years)</option>
                <option value="medium-term">Medium-term (3-10 years)</option>
                <option value="long-term">Long-term (10+ years)</option>
              </select>
            </div>
          </div>
        )}
      </div>

      <div className="form-actions">
        {step > 1 && (
          <button className="btn btn-secondary" onClick={() => setStep(step - 1)}>
            Previous
          </button>
        )}
        {step < 4 ? (
          <button className="btn btn-primary" onClick={() => setStep(step + 1)}>
            Next
          </button>
        ) : (
          <button className="btn btn-primary" onClick={handleSubmit}>
            Start Planning
          </button>
        )}
      </div>
    </div>
  );
};

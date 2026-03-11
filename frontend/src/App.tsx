import React, { useState, useEffect } from 'react';
import { IntakeForm } from '@/components/IntakeForm';
import { ChatInterface } from '@/components/ChatInterface';
import { BreakdownPanel } from '@/components/BreakdownPanel';
import { EvidencePanel } from '@/components/EvidencePanel';
import { apiClient } from '@/utils/api';
import type { UserProfile, ChatMessage, ChatResponse, Breakdown, Evidence } from '@/types';
import { Settings, User } from 'lucide-react';

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [hasProfile, setHasProfile] = useState(false);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [breakdown, setBreakdown] = useState<Breakdown>({});
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [modulesUsed, setModulesUsed] = useState<string[]>([]);
  const [showProfile, setShowProfile] = useState(false);

  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      const { session_id } = await apiClient.createSession();
      setSessionId(session_id);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const handleProfileSubmit = async (profile: UserProfile) => {
    if (!sessionId) return;

    try {
      await apiClient.createProfile(sessionId, profile);
      setUserProfile(profile);
      setHasProfile(true);
    } catch (error) {
      console.error('Failed to create profile:', error);
      alert('Failed to save profile. Please try again.');
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!sessionId) return;

    setMessages(prev => [...prev, { role: 'user', content: message }]);
    setIsLoading(true);

    try {
      const response: ChatResponse = await apiClient.sendMessage(sessionId, message);
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.response
      }]);
      
      setBreakdown(response.breakdown);
      setEvidence(response.evidence);
      setModulesUsed(response.modules_used);
    } catch (error: any) {
      console.error('Chat error:', error);
      const errorMessage = error.response?.data?.detail || 'An error occurred. Please try again.';
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${errorMessage}`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const resetProfile = () => {
    setShowProfile(false);
    setHasProfile(false);
    setUserProfile(null);
    setMessages([]);
    setBreakdown({});
    setEvidence([]);
    setModulesUsed([]);
    initializeSession();
  };

  if (!hasProfile && !showProfile) {
    return (
      <div className="app">
        <div className="container">
          <IntakeForm onSubmit={handleProfileSubmit} />
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>Family Office AI Agent</h1>
          <div className="header-actions">
            <button className="btn btn-icon" onClick={() => setShowProfile(!showProfile)} title="View Profile">
              <User size={20} />
            </button>
            <button className="btn btn-icon" onClick={resetProfile} title="Reset Profile">
              <Settings size={20} />
            </button>
          </div>
        </div>
      </header>

      <div className="main-content">
        {showProfile && userProfile && (
          <div className="profile-sidebar">
            <h3>Your Profile</h3>
            <div className="profile-details">
              <div className="profile-item">
                <strong>Age:</strong> {userProfile.age}
              </div>
              <div className="profile-item">
                <strong>Income:</strong> ${userProfile.income.toLocaleString()}
              </div>
              <div className="profile-item">
                <strong>Filing Status:</strong> {userProfile.filing_status}
              </div>
              <div className="profile-item">
                <strong>State:</strong> {userProfile.state}
              </div>
              {userProfile.family.children !== undefined && (
                <div className="profile-item">
                  <strong>Children:</strong> {userProfile.family.children}
                </div>
              )}
              <div className="profile-item">
                <strong>Risk Tolerance:</strong> {userProfile.risk_tolerance}
              </div>
            </div>
            <button className="btn btn-secondary" onClick={() => setShowProfile(false)}>
              Close Profile
            </button>
          </div>
        )}

        <div className={`chat-section ${showProfile ? 'sidebar-open' : ''}`}>
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </div>

        <div className="analysis-section">
          <BreakdownPanel breakdown={breakdown} modulesUsed={modulesUsed} />
          <EvidencePanel evidence={evidence} />
        </div>
      </div>
    </div>
  );
}

export default App;

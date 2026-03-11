import React, { useState } from 'react';
import { ChevronDown, ChevronRight, FileText } from 'lucide-react';
import type { Evidence } from '@/types';

interface EvidencePanelProps {
  evidence: Evidence[];
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ evidence }) => {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  if (!evidence || evidence.length === 0) {
    return null;
  }

  const toggleExpand = (docId: string) => {
    setExpandedIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(docId)) {
        newSet.delete(docId);
      } else {
        newSet.add(docId);
      }
      return newSet;
    });
  };

  return (
    <div className="evidence-panel">
      <h3>
        <FileText size={20} />
        Supporting Evidence ({evidence.length} sources)
      </h3>
      
      <div className="evidence-list">
        {evidence.map((item, idx) => {
          const isExpanded = expandedIds.has(item.doc_id);
          
          return (
            <div key={idx} className="evidence-item">
              <div className="evidence-header" onClick={() => toggleExpand(item.doc_id)}>
                <div className="evidence-icon">
                  {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                </div>
                <div className="evidence-meta">
                  <span className="doc-id">{item.doc_id}</span>
                  <span className="category">{item.category}</span>
                </div>
              </div>
              
              <div className="evidence-content">
                {isExpanded ? (
                  <div className="evidence-full">{item.full_text || item.snippet}</div>
                ) : (
                  <div className="evidence-snippet">{item.snippet}</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

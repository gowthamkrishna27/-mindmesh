import { useState } from 'react';
import type {
  Concept,
  StudentMastery,
  ResponseRecord
} from './data/mockData';
import {
  INITIAL_DIAGNOSTIC_MASTERY,
  POST_RETEST_MASTERY,
  DEMO_RESPONSES_HISTORY
} from './data/mockData';
import { ConceptGraphCanvas } from './components/ConceptGraphCanvas';
import { QuizView } from './components/QuizView';
import { EvidencePanel } from './components/EvidencePanel';
import { LearningPathView } from './components/LearningPathView';
import { RetestReportView } from './components/RetestReportView';
import { ConsentIntroView } from './components/ConsentIntroView';
import { ConceptDrawer } from './components/ConceptDrawer';
import { RotateCcw } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('graph');
  const [consentGiven, setConsentGiven] = useState<boolean>(true);

  // Application State
  const [masteryMap, setMasteryMap] = useState<Record<string, StudentMastery>>(INITIAL_DIAGNOSTIC_MASTERY);
  const [responses, setResponses] = useState<ResponseRecord[]>(DEMO_RESPONSES_HISTORY);
  const [selectedConcept, setSelectedConcept] = useState<Concept | null>(null);
  const [rootGapId, setRootGapId] = useState<string>('D12');

  const handleResponseSubmitted = (record: ResponseRecord) => {
    setResponses(prev => [record, ...prev]);

    setMasteryMap(prev => {
      const current = prev[record.concept_id] || {
        concept_id: record.concept_id,
        p: 0.5,
        n_direct: 0,
        n_indirect: 0,
        status: 'insufficient'
      };

      const p_bayes = record.correct ? 0.75 : 0.25;
      const w = record.evidence_weight || 1.0;
      let new_p = current.p + w * (p_bayes - current.p) * 0.4;
      new_p = Math.max(0.02, Math.min(0.98, new_p));

      const newDirect = current.n_direct + 1;
      let newStatus: 'insufficient' | 'suspected' | 'confirmed' | 'rejected' | 'mastered' = current.status;

      if (newDirect >= 2 && new_p > 0.70) newStatus = 'mastered';
      else if (newDirect >= 2 && new_p < 0.30) newStatus = 'confirmed';
      else if (!record.correct) newStatus = 'suspected';

      return {
        ...prev,
        [record.concept_id]: {
          ...current,
          p: Number(new_p.toFixed(2)),
          n_direct: newDirect,
          status: newStatus
        }
      };
    });
  };

  const handleResetDemo = () => {
    setMasteryMap(INITIAL_DIAGNOSTIC_MASTERY);
    setResponses(DEMO_RESPONSES_HISTORY);
    setRootGapId('D12');
    setActiveTab('intro');
  };

  const handleRetestCompleted = () => {
    setMasteryMap(POST_RETEST_MASTERY);
    setActiveTab('retest');
  };

  const tabs = [
    { id: 'intro', label: 'Overview' },
    { id: 'quiz', label: `Quiz (${responses.length}/12)` },
    { id: 'graph', label: 'Concept Graph' },
    { id: 'evidence', label: `Root Gap [${rootGapId}]` },
    { id: 'path', label: 'Learning Path' },
    { id: 'retest', label: 'Retest & Report' }
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f8fafc' }}>
      {/* Minimal Header */}
      <header style={{ background: '#ffffff', borderBottom: '1px solid #e2e8f0', position: 'sticky', top: 0, zIndex: 40 }}>
        <div className="app-container">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 0' }}>
            {/* Minimal Brand */}
            <div
              onClick={() => setActiveTab('intro')}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}
            >
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--primary)' }} />
              <span style={{ fontWeight: 700, fontSize: '16px', color: '#0f172a', letterSpacing: '-0.02em' }}>
                MindMesh
              </span>
              <span style={{ fontSize: '12px', color: '#94a3b8', borderLeft: '1px solid #e2e8f0', paddingLeft: '8px' }}>
                DBMS Prerequisite Graph
              </span>
            </div>

            {/* Subtle Actions */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <button
                onClick={() => {
                  setMasteryMap(INITIAL_DIAGNOSTIC_MASTERY);
                  setResponses(DEMO_RESPONSES_HISTORY);
                  setRootGapId('D12');
                  setActiveTab('evidence');
                }}
                className="btn-secondary"
                style={{ fontSize: '12px', padding: '5px 12px' }}
                title="Load seed demonstration scenario"
              >
                Load Seed Demo
              </button>

              <button
                onClick={handleResetDemo}
                className="btn-secondary"
                style={{ padding: '5px 8px' }}
                title="Reset session"
              >
                <RotateCcw size={13} />
              </button>
            </div>
          </div>

          {/* Understated Minimal Nav Tabs */}
          <nav style={{ display: 'flex', alignItems: 'center', gap: '2px', overflowX: 'auto', borderTop: '1px solid #f1f5f9', padding: '2px 0' }}>
            {tabs.map(tab => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  style={{
                    padding: '8px 12px',
                    fontSize: '12.5px',
                    fontWeight: isActive ? 600 : 500,
                    color: isActive ? 'var(--primary)' : '#64748b',
                    borderBottom: isActive ? '2px solid var(--primary)' : '2px solid transparent',
                    background: 'transparent',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    transition: 'color 0.1s ease'
                  }}
                >
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      {/* Main Container */}
      <main className="app-container" style={{ flex: 1, padding: '20px', width: '100%' }}>
        {activeTab === 'intro' && (
          <ConsentIntroView
            onStartQuiz={() => setActiveTab('quiz')}
            consentGiven={consentGiven}
            setConsentGiven={setConsentGiven}
          />
        )}

        {activeTab === 'quiz' && (
          <QuizView
            onResponseSubmitted={handleResponseSubmitted}
            currentMastery={masteryMap}
            responses={responses}
          />
        )}

        {activeTab === 'graph' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
              <div>
                <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>Prerequisite Dependency Graph</h2>
                <p style={{ fontSize: '12.5px', color: '#64748b' }}>
                  Directed flow: A → B means A is a prerequisite of B. Click any node to inspect.
                </p>
              </div>
              <button
                onClick={() => setActiveTab('evidence')}
                className="btn-secondary"
                style={{ fontSize: '12px', padding: '6px 12px' }}
              >
                Inspect Root Gap
              </button>
            </div>

            <ConceptGraphCanvas
              masteryMap={masteryMap}
              selectedConceptId={selectedConcept?.id || null}
              onSelectConcept={concept => setSelectedConcept(concept)}
              rootGapId={rootGapId}
            />
          </div>
        )}

        {activeTab === 'evidence' && (
          <EvidencePanel
            masteryMap={masteryMap}
            responses={responses}
            rootGapId={rootGapId}
          />
        )}

        {activeTab === 'path' && (
          <LearningPathView
            onUnlockRetest={handleRetestCompleted}
          />
        )}

        {activeTab === 'retest' && (
          <RetestReportView
            onResetDemo={handleResetDemo}
          />
        )}
      </main>

      {/* Concept Drawer */}
      <ConceptDrawer
        concept={selectedConcept}
        mastery={selectedConcept ? masteryMap[selectedConcept.id] : undefined}
        onClose={() => setSelectedConcept(null)}
        onTestConcept={() => {
          setActiveTab('quiz');
        }}
      />

      {/* Minimal Footer */}
      <footer style={{ borderTop: '1px solid #e2e8f0', background: '#ffffff', padding: '12px 0', fontSize: '11.5px', color: '#94a3b8' }}>
        <div className="app-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
          <div>
            MindMesh • AI-VERSE 30
          </div>
          <div>
            A → B (A is prerequisite of B)
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

'use client';

import React, { useEffect, useState } from 'react';
import { Concept, StudentMastery, ResponseRecord } from '@/lib/types';
import { fetchConcepts } from '@/lib/apiClient';
import { ConceptGraph } from './concept-graph';
import { EvidenceDrawer } from './evidence-drawer';
import { WrongQuestionsReview } from './wrong-questions-review';
import { Button } from '@/components/ui/button';
import {
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  Layers,
  ArrowRight
} from 'lucide-react';

interface DiagnosisReportProps {
  masteryMap: Record<string, StudentMastery>;
  responses: ResponseRecord[];
  rootGapId: string;
  onGoToRoadmap?: () => void;
  onRetest: () => void;
  isDark: boolean;
  concepts?: Concept[];
}

export function DiagnosisReport({
  masteryMap,
  responses,
  rootGapId,
  onGoToRoadmap,
  onRetest,
  isDark,
  concepts: initialConcepts
}: DiagnosisReportProps) {
  const [selectedConcept, setSelectedConcept] = useState<Concept | null>(null);
  const [concepts, setConcepts] = useState<Concept[]>(initialConcepts || []);

  useEffect(() => {
    if (!initialConcepts || initialConcepts.length === 0) {
      fetchConcepts().then(c => {
        if (c && c.length > 0) setConcepts(c);
      });
    }
  }, [initialConcepts]);

  const masteredConcepts = concepts.filter(c => masteryMap[c.id]?.status === 'mastered');
  const gapConcepts = concepts.filter(
    c => masteryMap[c.id]?.status === 'confirmed' || masteryMap[c.id]?.status === 'suspected'
  );
  const uncertainConcepts = concepts.filter(
    c => masteryMap[c.id]?.status === 'insufficient' || masteryMap[c.id]?.status === 'uncertain' || (!masteryMap[c.id] && c.id !== rootGapId)
  );

  return (
    <div className="space-y-6">

      {/* Summary KPI Strip */}
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border bg-card p-4 text-center shadow-xs">
          <div className="flex items-center justify-center text-emerald-600 mb-1">
            <CheckCircle2 className="size-4" />
          </div>
          <p className="text-2xl font-bold">{masteredConcepts.length}</p>
          <p className="text-xs text-muted-foreground font-medium uppercase mt-0.5">Mastered</p>
        </div>

        <div className="rounded-xl border bg-card p-4 text-center shadow-xs">
          <div className="flex items-center justify-center text-rose-600 mb-1">
            <AlertTriangle className="size-4" />
          </div>
          <p className="text-2xl font-bold">{gapConcepts.length}</p>
          <p className="text-xs text-muted-foreground font-medium uppercase mt-0.5">Identified Gaps</p>
        </div>

        <div className="rounded-xl border bg-card p-4 text-center shadow-xs">
          <div className="flex items-center justify-center text-amber-600 mb-1">
            <HelpCircle className="size-4" />
          </div>
          <p className="text-2xl font-bold">{uncertainConcepts.length}</p>
          <p className="text-xs text-muted-foreground font-medium uppercase mt-0.5">Untested / Other</p>
        </div>
      </div>

      {/* Action Bar (Retake removed, focused on learning prerequisites & retesting) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-xl border bg-card p-3.5 sm:p-4 shadow-xs">
        <div>
          <h2 className="text-sm font-bold">Diagnostic Findings &amp; Next Steps</h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            {rootGapId
              ? `Root blocker isolated at ${rootGapId}. Review the prerequisite gaps below, study the material, and verify with a retest.`
              : 'Review your performance and prerequisite requirements below.'}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {onGoToRoadmap && (
            <Button variant="outline" size="sm" onClick={onGoToRoadmap} className="text-xs gap-1.5 w-full sm:w-auto">
              <Layers className="size-3.5 text-primary" />
              View Study Roadmap
            </Button>
          )}
          <Button size="sm" onClick={onRetest} className="text-xs gap-1.5 w-full sm:w-auto">
            <CheckCircle2 className="size-3.5" />
            Take Verification Retest
          </Button>
        </div>
      </div>

      {/* Prominent Incorrect Questions & Prerequisites Analysis */}
      <WrongQuestionsReview
        responses={responses}
        concepts={concepts}
        masteryMap={masteryMap}
        onSelectConcept={c => setSelectedConcept(c)}
        onGoToRoadmap={onGoToRoadmap}
      />

      {/* Interactive Concept Graph Canvas */}
      <div className="rounded-xl border bg-card p-4 shadow-xs space-y-2">
        <div className="flex items-center justify-between pb-1">
          <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            Prerequisite Knowledge Graph
          </h3>
          <span className="text-[11px] text-muted-foreground">
            Click any concept node to inspect evidence and prerequisite dependencies
          </span>
        </div>
        <ConceptGraph
          masteryMap={masteryMap}
          selectedConceptId={selectedConcept?.id || null}
          onSelectConcept={c => setSelectedConcept(c)}
          rootGapId={rootGapId}
          isDark={isDark}
          concepts={concepts}
        />
      </div>

      {/* Evidence Drawer for Selected Concept */}
      <EvidenceDrawer
        concept={selectedConcept}
        mastery={selectedConcept ? masteryMap[selectedConcept.id] : undefined}
        responses={responses}
        isRootGap={selectedConcept?.id === rootGapId}
        onClose={() => setSelectedConcept(null)}
        onGoToRoadmap={onGoToRoadmap}
        allConcepts={concepts}
      />
    </div>
  );
}

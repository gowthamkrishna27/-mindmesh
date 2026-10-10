'use client';

import React, { useEffect, useState } from 'react';
import { Concept, StudentMastery, ResponseRecord } from '@/lib/types';
import { fetchConcepts } from '@/lib/apiClient';
import { X, ExternalLink, AlertCircle, CheckCircle2, ArrowRight, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface EvidenceDrawerProps {
  concept: Concept | null;
  mastery: StudentMastery | undefined;
  responses: ResponseRecord[];
  isRootGap: boolean;
  onClose: () => void;
  onGoToRoadmap?: () => void;
  allConcepts?: Concept[];
}

export function EvidenceDrawer({
  concept,
  mastery,
  responses,
  isRootGap,
  onClose,
  onGoToRoadmap,
  allConcepts: initialConcepts
}: EvidenceDrawerProps) {
  const [concepts, setConcepts] = useState<Concept[]>(initialConcepts || []);

  useEffect(() => {
    if (!initialConcepts || initialConcepts.length === 0) {
      fetchConcepts().then(c => {
        if (c && c.length > 0) setConcepts(c);
      });
    } else {
      setConcepts(initialConcepts);
    }
  }, [initialConcepts]);

  if (!concept) return null;

  // Filter responses relating directly to this concept or distractors mapped to it
  const relatedResponses = responses.filter(
    r => r.concept_id === concept.id || r.distractor_mapped_to === concept.id
  );

  const prereqConcepts = (concept.prerequisites || [])
    .map(id => concepts.find(c => c.id === id))
    .filter(Boolean) as Concept[];

  const dependentConcepts = concepts.filter(c => (c.prerequisites || []).includes(concept.id));

  return (
    <div className="rounded-lg border bg-card p-6 shadow-sm">
      <div className="flex items-start justify-between border-b pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-sm font-bold text-primary">{concept.id}</span>
            <h3 className="text-lg font-bold">{concept.name}</h3>
            {isRootGap && (
              <span className="rounded bg-rose-100 px-2 py-0.5 text-xs font-semibold text-rose-700 dark:bg-rose-950 dark:text-rose-300">
                Target Blocker
              </span>
            )}
          </div>
          <p className="mt-1 text-sm text-muted-foreground">{concept.description}</p>
        </div>
        <button
          onClick={onClose}
          className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
          aria-label="Close evidence panel"
        >
          <X className="size-5" />
        </button>
      </div>

      <div className="mt-4 grid gap-6 md:grid-cols-2">
        {/* Left Column: Mastery State & Evidence */}
        <div className="space-y-4">
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Mastery Assessment
            </h4>
            <div className="mt-2 flex items-center gap-3">
              <span className="text-2xl font-bold">
                {mastery ? Math.round(mastery.p * 100) : 50}%
              </span>
              <span className="text-xs text-muted-foreground">
                Confidence probability (p-value)
              </span>
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              Direct evidence: {mastery?.n_direct ?? 0} answers &middot; Indirect evidence:{' '}
              {mastery?.n_indirect ?? 0} answers
            </div>
          </div>

          {/* Diagnostic Evidence Log */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Direct Diagnostic Evidence
            </h4>
            {relatedResponses.length > 0 ? (
              <div className="mt-2 space-y-2">
                {relatedResponses.map(r => (
                  <div
                    key={r.id}
                    className="flex items-start gap-2.5 rounded-lg border bg-muted/30 p-3 text-xs"
                  >
                    {r.correct ? (
                      <CheckCircle2 className="mt-0.5 size-4 text-emerald-600 shrink-0" />
                    ) : (
                      <AlertCircle className="mt-0.5 size-4 text-rose-600 shrink-0" />
                    )}
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold">{r.question_id}</span>
                        <span className="text-[10px] text-muted-foreground">{r.timestamp}</span>
                      </div>
                      <p className="text-muted-foreground">
                        Confidence: <strong className="text-foreground">{r.confidence}</strong> &middot; Time:{' '}
                        {(r.response_ms / 1000).toFixed(1)}s
                      </p>
                      {r.misconception && (
                        <p className="text-rose-600 dark:text-rose-400 font-medium">
                          Identified Misconception: {r.misconception}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="mt-2 text-xs text-muted-foreground">
                No direct question responses logged for this concept yet. Status inferred from DAG prerequisite dependencies.
              </p>
            )}
          </div>
        </div>

        {/* Right Column: DAG Hierarchy & Next Steps */}
        <div className="space-y-4">
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Prerequisite Foundations
            </h4>
            {prereqConcepts.length > 0 ? (
              <div className="mt-2 space-y-1.5">
                {prereqConcepts.map(p => (
                  <div
                    key={p.id}
                    className="flex items-center justify-between rounded border bg-background px-3 py-2 text-xs"
                  >
                    <div>
                      <span className="font-mono font-bold text-muted-foreground mr-2">{p.id}</span>
                      <span className="font-medium">{p.name}</span>
                    </div>
                    <span className="text-[11px] text-muted-foreground">Prerequisite</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="mt-2 text-xs text-muted-foreground">
                This is a root foundation concept with no upstream prerequisites.
              </p>
            )}
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Downstream Dependent Topics
            </h4>
            {dependentConcepts.length > 0 ? (
              <div className="mt-2 space-y-1.5">
                {dependentConcepts.map(d => (
                  <div
                    key={d.id}
                    className="flex items-center justify-between rounded border bg-background px-3 py-2 text-xs"
                  >
                    <div>
                      <span className="font-mono font-bold text-muted-foreground mr-2">{d.id}</span>
                      <span className="font-medium">{d.name}</span>
                    </div>
                    <span className="text-[11px] text-muted-foreground">Blocked Downstream</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="mt-2 text-xs text-muted-foreground">
                No downstream concepts depend on this topic.
              </p>
            )}
          </div>

          {concept.resources && concept.resources.length > 0 && (
            <div className="pt-2 space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Targeted Learning Resources
              </h4>
              <div className="space-y-2">
                {concept.resources.map((res, i) => (
                  <a
                    key={i}
                    href={res.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block rounded-lg border bg-background p-3 text-xs hover:border-primary/50 transition-colors"
                  >
                    <div className="flex items-center justify-between font-semibold text-primary">
                      <span>{res.title}</span>
                      <ExternalLink className="size-3.5 shrink-0" />
                    </div>
                    {res.summary && (
                      <p className="mt-1 text-[11px] text-muted-foreground line-clamp-2">
                        {res.summary}
                      </p>
                    )}
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

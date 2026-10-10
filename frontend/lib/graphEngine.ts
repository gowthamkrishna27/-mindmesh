import { Concept, StudentMastery } from './types';

export interface ResponseInput {
  question_id: string;
  concept_id: string;
  option_id?: string;
  confidence?: 'low' | 'medium' | 'high';
  response_ms?: number;
  correct?: boolean;
}

export interface GraphNodeData {
  id: string;
  name: string;
  difficulty: number;
  tier: number;
  in_degree: number;
  out_degree: number;
  ancestor_count: number;
  descendant_count: number;
  importance: number;
}

export interface DiagnosisResult {
  target_failed_concept: string;
  root_gap_id: string;
  root_gap_name: string;
  evidence_path: string[];
  mastery_map: Record<string, StudentMastery>;
  confirmed_gaps: string[];
  suspected_gaps: string[];
  mastered: string[];
  explanation: string;
}

export interface LearningRoadmapStep {
  position: number;
  concept_id: string;
  concept_name: string;
  prerequisites: string[];
  rationale: string;
  estimated_mins: number;
  resources: any[];
}

/**
 * MindMesh Directed Acyclic Graph (DAG) Engine
 * Implements FR-G1 through FR-G6 and SRS Section 5 Bayesian Diagnostic Inference.
 */
export class ConceptGraphEngine {
  private conceptsMap: Map<string, Concept> = new Map();
  // Adjacency: source -> set of targets (prereq -> dependent)
  private forwardAdj: Map<string, Set<string>> = new Map();
  // Reverse: target -> set of sources (dependent -> prereqs)
  private reverseAdj: Map<string, Set<string>> = new Map();

  constructor(concepts: Concept[] = []) {
    if (concepts.length > 0) {
      this.loadConcepts(concepts);
    }
  }

  /**
   * FR-G1: Build Directed Acyclic Graph from concepts list
   */
  public loadConcepts(concepts: Concept[]): void {
    this.conceptsMap.clear();
    this.forwardAdj.clear();
    this.reverseAdj.clear();

    for (const c of concepts) {
      this.conceptsMap.set(c.id, c);
      this.forwardAdj.set(c.id, new Set());
      this.reverseAdj.set(c.id, new Set());
    }

    for (const c of concepts) {
      for (const prereqId of c.prerequisites || []) {
        if (this.conceptsMap.has(prereqId)) {
          this.forwardAdj.get(prereqId)!.add(c.id);
          this.reverseAdj.get(c.id)!.add(prereqId);
        }
      }
    }

    this.validateGraph();
  }

  /**
   * FR-G2: Graph validation (Cycles, Self-loops, Dangling prerequisites)
   */
  public validateGraph(): { isValidDAG: boolean; errors: string[] } {
    const errors: string[] = [];

    // 1. Self loops
    for (const [node, targets] of this.forwardAdj.entries()) {
      if (targets.has(node)) {
        errors.push(`Self-loop detected on concept '${node}'`);
      }
    }

    // 2. Dangling prerequisites
    for (const [node, prereqs] of this.reverseAdj.entries()) {
      for (const p of prereqs) {
        if (!this.conceptsMap.has(p)) {
          errors.push(`Dangling prerequisite '${p}' required by '${node}'`);
        }
      }
    }

    // 3. Cycle Detection via DFS (coloring: 0=unvisited, 1=visiting, 2=visited)
    const state = new Map<string, number>();
    for (const node of this.conceptsMap.keys()) {
      state.set(node, 0);
    }

    let hasCycle = false;
    const dfsCycle = (curr: string) => {
      state.set(curr, 1);
      for (const next of this.forwardAdj.get(curr) || []) {
        if (state.get(next) === 1) {
          hasCycle = true;
          errors.push(`Cycle detected involving edge '${curr}' -> '${next}'`);
        } else if (state.get(next) === 0) {
          dfsCycle(next);
        }
      }
      state.set(curr, 2);
    };

    for (const node of this.conceptsMap.keys()) {
      if (state.get(node) === 0) {
        dfsCycle(node);
      }
    }

    return {
      isValidDAG: errors.length === 0 && !hasCycle,
      errors
    };
  }

  /**
   * Direct prerequisites (parents in prerequisite direction)
   */
  public getPrerequisites(conceptId: string): string[] {
    return Array.from(this.reverseAdj.get(conceptId) || []);
  }

  /**
   * Direct dependents (children unlocked by this prerequisite)
   */
  public getDependents(conceptId: string): string[] {
    return Array.from(this.forwardAdj.get(conceptId) || []);
  }

  /**
   * FR-G3: Returns all ancestors (foundational prerequisites) with shortest distance
   */
  public getAncestorsWithDistance(conceptId: string): Record<string, number> {
    const distances: Record<string, number> = {};
    if (!this.conceptsMap.has(conceptId)) return distances;

    const queue: Array<{ id: string; dist: number }> = [];
    const visited = new Set<string>();

    for (const prereq of this.getPrerequisites(conceptId)) {
      queue.push({ id: prereq, dist: 1 });
      visited.add(prereq);
    }

    while (queue.length > 0) {
      const { id, dist } = queue.shift()!;
      distances[id] = dist;

      for (const parent of this.getPrerequisites(id)) {
        if (!visited.has(parent)) {
          visited.add(parent);
          queue.push({ id: parent, dist: dist + 1 });
        }
      }
    }

    return distances;
  }

  /**
   * Returns all descendants (downstream concepts unlocked)
   */
  public getDescendants(conceptId: string): Set<string> {
    const descendants = new Set<string>();
    if (!this.conceptsMap.has(conceptId)) return descendants;

    const queue: string[] = [...this.getDependents(conceptId)];
    for (const d of queue) descendants.add(d);

    while (queue.length > 0) {
      const curr = queue.shift()!;
      for (const next of this.getDependents(curr)) {
        if (!descendants.has(next)) {
          descendants.add(next);
          queue.push(next);
        }
      }
    }

    return descendants;
  }

  /**
   * FR-G5: Downstream descendant share: |descendants(c)| / |total_concepts|
   */
  public computeImportance(conceptId: string): number {
    const total = this.conceptsMap.size;
    if (total === 0 || !this.conceptsMap.has(conceptId)) return 0;
    const descendants = this.getDescendants(conceptId);
    return Number((descendants.size / total).toFixed(3));
  }

  /**
   * FR-G4: Return valid learning order (topological sort) via Kahn's algorithm
   */
  public getTopologicalSort(subsetIds?: string[]): string[] {
    const validSet = subsetIds ? new Set(subsetIds.filter(id => this.conceptsMap.has(id))) : new Set(this.conceptsMap.keys());
    const inDegree = new Map<string, number>();

    for (const node of validSet) {
      inDegree.set(node, 0);
    }

    for (const node of validSet) {
      for (const target of this.forwardAdj.get(node) || []) {
        if (validSet.has(target)) {
          inDegree.set(target, (inDegree.get(target) || 0) + 1);
        }
      }
    }

    const queue: string[] = [];
    for (const [node, deg] of inDegree.entries()) {
      if (deg === 0) queue.push(node);
    }

    const order: string[] = [];
    while (queue.length > 0) {
      const u = queue.shift()!;
      order.push(u);

      for (const v of this.forwardAdj.get(u) || []) {
        if (validSet.has(v)) {
          const newDeg = (inDegree.get(v) || 0) - 1;
          inDegree.set(v, newDeg);
          if (newDeg === 0) queue.push(v);
        }
      }
    }

    return order;
  }

  /**
   * FR-G6: Minimal DAG edge representation for uncluttered visual layouts (Transitive Reduction)
   */
  public getTransitiveReduction(): Array<{ source: string; target: string }> {
    const allEdges: Array<{ source: string; target: string }> = [];
    for (const [source, targets] of this.forwardAdj.entries()) {
      for (const target of targets) {
        allEdges.push({ source, target });
      }
    }

    // Check if there is a path of length >= 2 between source and target
    const reducedEdges: Array<{ source: string; target: string }> = [];

    for (const edge of allEdges) {
      // Find if alternative path exists from edge.source to edge.target without using edge directly
      const hasAlternative = this.hasPathExcludingEdge(edge.source, edge.target);
      if (!hasAlternative) {
        reducedEdges.push(edge);
      }
    }

    return reducedEdges;
  }

  private hasPathExcludingEdge(source: string, target: string): boolean {
    const queue: string[] = [];
    const visited = new Set<string>();

    for (const neighbor of this.forwardAdj.get(source) || []) {
      if (neighbor !== target) {
        queue.push(neighbor);
        visited.add(neighbor);
      }
    }

    while (queue.length > 0) {
      const curr = queue.shift()!;
      if (curr === target) return true;

      for (const next of this.forwardAdj.get(curr) || []) {
        if (!visited.has(next)) {
          visited.add(next);
          queue.push(next);
        }
      }
    }

    return false;
  }

  /**
   * Shortest path between two nodes in the DAG
   */
  public getShortestPath(source: string, target: string): string[] {
    if (source === target) return [source];
    const queue: Array<{ node: string; path: string[] }> = [{ node: source, path: [source] }];
    const visited = new Set<string>([source]);

    while (queue.length > 0) {
      const { node, path } = queue.shift()!;
      for (const next of this.forwardAdj.get(node) || []) {
        if (next === target) {
          return [...path, next];
        }
        if (!visited.has(next)) {
          visited.add(next);
          queue.push({ node: next, path: [...path, next] });
        }
      }
    }

    return [source, target];
  }

  /**
   * Bayesian belief updating per SRS Section 5.2
   */
  public updateMasteryState(responses: ResponseInput[]): Record<string, StudentMastery> {
    const mastery: Record<string, StudentMastery> = {};

    for (const cid of this.conceptsMap.keys()) {
      mastery[cid] = {
        concept_id: cid,
        p: 0.50,
        n_direct: 0,
        n_indirect: 0,
        status: 'insufficient',
        blocker_score: 0.0,
        uncertainty: 1.0
      };
    }

    const s = 0.10; // slip
    const g = 0.20; // guess

    for (const resp of responses) {
      const cid = resp.concept_id;
      if (!cid || !mastery[cid]) continue;

      const correct = !!resp.correct;
      const confidence = resp.confidence || 'medium';
      const responseMs = resp.response_ms || 1500;

      let w = 1.0;
      if (confidence === 'high') {
        w = correct ? 1.25 : 1.35;
      } else if (confidence === 'low') {
        w = 0.75;
      }

      if (responseMs < 2000 && !correct) {
        w *= 1.15;
      }

      const currP = mastery[cid].p;

      let newP = currP;
      if (correct) {
        const pC = currP * (1 - s) + (1 - currP) * g;
        const post = (currP * (1 - s)) / (pC > 0 ? pC : 0.001);
        newP = currP + (post - currP) * (0.8 * w);
      } else {
        const pInc = currP * s + (1 - currP) * (1 - g);
        const post = (currP * s) / (pInc > 0 ? pInc : 0.001);
        newP = currP + (post - currP) * (0.9 * w);
      }

      mastery[cid].p = Math.max(0.02, Math.min(0.98, Number(newP.toFixed(4))));
      mastery[cid].n_direct += 1;

      // Prerequisite propagation
      const prereqs = this.getPrerequisites(cid);
      for (const pr of prereqs) {
        if (mastery[pr]) {
          if (!correct) {
            mastery[pr].p = Math.max(0.05, Number((mastery[pr].p - 0.12 * w).toFixed(4)));
            mastery[pr].n_indirect += 1;
          } else {
            mastery[pr].p = Math.min(0.95, Number((mastery[pr].p + 0.05 * w).toFixed(4)));
            mastery[pr].n_indirect += 1;
          }
        }
      }
    }

    // Classify status per SRS Section 5.3
    for (const [cid, m] of Object.entries(mastery)) {
      const p = m.p;
      const nDirect = m.n_direct;
      const importance = this.computeImportance(cid);
      m.blocker_score = Number(((1.0 - p) * importance).toFixed(4));
      m.uncertainty = Number((1.0 - Math.abs(2.0 * p - 1.0)).toFixed(3));

      if (p >= 0.70 && nDirect >= 1) {
        m.status = p >= 0.85 ? 'mastered' : 'rejected';
      } else if (p < 0.30 && nDirect >= 2) {
        m.status = 'confirmed';
      } else if (p < 0.50 || m.n_indirect > 0) {
        m.status = 'suspected';
      } else {
        m.status = 'insufficient';
      }
    }

    return mastery;
  }

  /**
   * SRS Section 5.4: Root-Gap Selection using NetworkX DAG principles
   */
  public diagnoseRootGap(responses: ResponseInput[]): DiagnosisResult {
    const mastery = this.updateMasteryState(responses);

    const failedConcepts = responses.filter(r => !r.correct).map(r => r.concept_id);
    const targetFailed = failedConcepts[failedConcepts.length - 1] || 'D13';

    const ancestorsDist = this.getAncestorsWithDistance(targetFailed);
    const ancestorCandidates = Object.keys(ancestorsDist).filter(
      cid => mastery[cid]?.status === 'confirmed' || mastery[cid]?.status === 'suspected'
    );

    let rootGapId = targetFailed;
    let evidencePath: string[] = [targetFailed];

    if (ancestorCandidates.length > 0) {
      ancestorCandidates.sort((a, b) => {
        const scoreA = mastery[a]?.blocker_score || 0;
        const scoreB = mastery[b]?.blocker_score || 0;
        if (scoreB !== scoreA) return scoreB - scoreA;
        return (ancestorsDist[b] || 0) - (ancestorsDist[a] || 0);
      });
      rootGapId = ancestorCandidates[0];
      evidencePath = this.getShortestPath(rootGapId, targetFailed);
    }

    const rootConcept = this.conceptsMap.get(rootGapId);
    const targetConcept = this.conceptsMap.get(targetFailed);
    const rootName = rootConcept?.name || rootGapId;
    const targetName = targetConcept?.name || targetFailed;

    const downstreamCount = this.getDescendants(rootGapId).size;

    const explanation = `Failure on '${targetName}' was traced via prerequisite graph to foundational concept '${rootName}'. Resolving '${rootName}' unlocks ${downstreamCount} downstream concepts in the DBMS curriculum.`;

    return {
      target_failed_concept: targetFailed,
      root_gap_id: rootGapId,
      root_gap_name: rootName,
      evidence_path: evidencePath,
      mastery_map: mastery,
      confirmed_gaps: Object.keys(mastery).filter(cid => mastery[cid].status === 'confirmed'),
      suspected_gaps: Object.keys(mastery).filter(cid => mastery[cid].status === 'suspected'),
      mastered: Object.keys(mastery).filter(cid => mastery[cid].status === 'mastered' || mastery[cid].status === 'rejected'),
      explanation
    };
  }

  /**
   * FR-G4: Topologically sorted learning path for remediating gaps
   */
  public generateLearningRoadmap(gapIds: string[]): LearningRoadmapStep[] {
    const allRemediationNodes = new Set<string>(gapIds);

    for (const gid of gapIds) {
      if (this.conceptsMap.has(gid)) {
        const ancestors = this.getAncestorsWithDistance(gid);
        for (const anc of Object.keys(ancestors)) {
          allRemediationNodes.add(anc);
        }
      }
    }

    const sortedIds = this.getTopologicalSort(Array.from(allRemediationNodes));

    return sortedIds.map((cid, idx) => {
      const cInfo = this.conceptsMap.get(cid);
      const prereqs = this.getPrerequisites(cid);
      const prereqNames = prereqs.map(p => this.conceptsMap.get(p)?.name || p);

      const rationale =
        prereqs.length === 0
          ? `Foundational requirement for ${cInfo?.name || cid}.`
          : `Builds directly upon completed foundations: ${prereqNames.join(', ')}.`;

      return {
        position: idx + 1,
        concept_id: cid,
        concept_name: cInfo?.name || cid,
        prerequisites: prereqs,
        rationale,
        estimated_mins: 15 + (cInfo?.difficulty || 1) * 5,
        resources: cInfo?.resources || []
      };
    });
  }

  /**
   * Full Graph Data payload matching BackendGraphResponse
   */
  public getGraphData(): {
    nodes: GraphNodeData[];
    edges: Array<{ source: string; target: string }>;
    transitive_reduced_edges: Array<{ source: string; target: string }>;
    topological_order: string[];
    is_valid_dag: boolean;
  } {
    const nodes: GraphNodeData[] = [];

    for (const [id, c] of this.conceptsMap.entries()) {
      nodes.push({
        id,
        name: c.name,
        difficulty: c.difficulty,
        tier: c.tier || 1,
        in_degree: this.reverseAdj.get(id)?.size || 0,
        out_degree: this.forwardAdj.get(id)?.size || 0,
        ancestor_count: Object.keys(this.getAncestorsWithDistance(id)).length,
        descendant_count: this.getDescendants(id).size,
        importance: this.computeImportance(id)
      });
    }

    const edges: Array<{ source: string; target: string }> = [];
    for (const [source, targets] of this.forwardAdj.entries()) {
      for (const target of targets) {
        edges.push({ source, target });
      }
    }

    return {
      nodes,
      edges,
      transitive_reduced_edges: this.getTransitiveReduction(),
      topological_order: this.getTopologicalSort(),
      is_valid_dag: this.validateGraph().isValidDAG
    };
  }
}

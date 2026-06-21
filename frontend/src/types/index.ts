export interface ArtifactSection {
  id: string;
  title: string;
  content: string; // Plain-language ELI5 translation
  citations: string[]; // List of source citation strings
  isExpandedByDefault?: boolean;
}

export interface ArtifactAction {
  id: string;
  label: string; // e.g., "Check doctor network"
  type: 'chat_prompt' | 'calculator' | 'form_download' | 'external_link';
  payload: string; // pre-filled chat query or resource URL
}

export interface ArtifactPreview {
  badge: string; // e.g., "Plan Financials"
  heroStat?: string; // e.g., "$1,250"
  secondaryStat?: string; // e.g., "In-Network Deductible"
  shortDescription: string; // ELI5 summary preview
  quickAction: ArtifactAction; // Level 1 CTA
}

export interface Artifact {
  id: string;
  name: string; // e.g., "Your Share of Costs"
  type: 'policy_summary' | 'scenario_analysis';
  version: string;
  preview: ArtifactPreview;
  sections: ArtifactSection[];
  deepCTAs: ArtifactAction[]; // Level 2 CTAs
  lastUpdated: string;
}

export interface ArtifactReference {
  artifactId: string;
  sectionId?: string;
  highlightedTextSnippet?: string;
}

export interface ArtifactState {
  currentView: 'upload' | 'discovery' | 'workspace';
  activeArtifactId: string | null;
  expandedSectionIds: Record<string, string[]>; // artifactId -> sectionIds
  highlightedReference: ArtifactReference | null;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'mike';
  text: string;
  decision?: 'likely_covered' | 'conditionally_covered' | 'likely_not_covered' | 'unknown';
  detailedReasoning?: string;
  conditions?: string[];
  nextSteps?: string[];
  referencedArtifactIds?: string[];
}

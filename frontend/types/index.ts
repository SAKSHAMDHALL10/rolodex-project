export interface ExperienceItem {
  title: string;
  company: string;
  start_date?: string | null;
  end_date?: string | null;
  description?: string | null;
}

export interface EducationItem {
  school: string;
  degree?: string | null;
  field_of_study?: string | null;
  start_year?: string | null;
  end_year?: string | null;
}

export type ConnectionNoteType =
  | "met_at_hackathon"
  | "worked_together"
  | "referral"
  | "investor"
  | "mentor"
  | "mutual_connection"
  | "future_collaboration"
  | "other";

export interface ConnectionNote {
  note_type: ConnectionNoteType;
  text: string;
  created_at: string;
}

export interface ContactListItem {
  id: string;
  full_name: string;
  headline?: string | null;
  current_company?: string | null;
  current_title?: string | null;
  location?: string | null;
  relevance_tags: string[];
  created_at: string;
}

export interface ContactRead {
  id: string;
  full_name: string;
  headline?: string | null;
  linkedin_url?: string | null;
  photo_url?: string | null;
  current_company?: string | null;
  current_title?: string | null;
  location?: string | null;
  industry?: string | null;
  summary?: string | null;
  experience: ExperienceItem[];
  education: EducationItem[];
  skills: string[];
  technologies: string[];
  domains: string[];
  capabilities: string[];
  interests: string[];
  relevance_summary?: string | null;
  relevance_tags: string[];
  connection_notes: ConnectionNote[];
  source_type?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DuplicateCandidate {
  contact: ContactListItem;
  match_reasons: string[];
  similarity_score: number;
}

export interface IngestResponse {
  status: "created" | "possible_duplicate";
  contact?: ContactRead | null;
  duplicates: DuplicateCandidate[];
}

export interface SearchFilters {
  role?: string | null;
  company?: string | null;
  industry?: string | null;
  skills: string[];
  technologies: string[];
  tags: string[];
  location?: string | null;
}

export interface SearchResultItem {
  contact: ContactListItem;
  score?: number | null;
  matched_on: string[];
}

export interface SearchResponse {
  query?: string | null;
  interpreted_filters: SearchFilters;
  results: SearchResultItem[];
  total: number;
}

export interface TopCount {
  name: string;
  count: number;
}

export interface DashboardStats {
  total_contacts: number;
  recent_contacts: ContactListItem[];
  top_skills: TopCount[];
  top_industries: TopCount[];
  top_tags: TopCount[];
  recent_searches: string[];
}

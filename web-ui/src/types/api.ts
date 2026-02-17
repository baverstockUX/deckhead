import { DeckStructure, ClarificationQuestion, ClarificationResponse } from './models';

// API Request Types
export interface CreateSessionRequest {}

export interface ParseContentRequest {
  session_id: string;
  content: string;
  mode: 'minimal' | 'rich';
}

export interface RefineStructureRequest {
  session_id: string;
  clarifications: ClarificationResponse[];
}

export interface StartGenerationRequest {
  session_id: string;
}

// API Response Types
export interface CreateSessionResponse {
  session_id: string;
}

export interface UploadFileResponse {
  file_id: string;
  filename: string;
}

export interface ParseContentResponse {
  deck_structure: DeckStructure;
  clarification_questions: ClarificationQuestion[];
}

export interface RefineStructureResponse {
  deck_structure: DeckStructure;
}

export interface StartGenerationResponse {
  job_id: string;
  message: string;
}

export interface GenerationStatusResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  message?: string;
  output_path?: string;
  error?: string;
}

export interface APIError {
  detail: string;
}

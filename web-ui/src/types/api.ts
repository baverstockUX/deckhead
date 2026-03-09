import { DeckStructure, ClarificationQuestion, ClarificationResponse } from './models';

// API Request Types
export interface ParseContentRequest {
  content: string;
  mode: 'minimal' | 'rich';
}

export interface RefineStructureRequest {
  deck_structure: DeckStructure;
  clarifications: ClarificationResponse[];
  mode: 'minimal' | 'rich';
}

export interface StartGenerationRequest {
  deck_structure: DeckStructure;
  brand_asset_file_ids: string[];
}

// API Response Types
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

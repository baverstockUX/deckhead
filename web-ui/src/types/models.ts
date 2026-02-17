// Type definitions mirroring Python Pydantic models

export interface TextContent {
  bullets?: string[] | null;
  statistics?: Array<{ [key: string]: string }> | null;
  paragraphs?: string[] | null;
  callouts?: Array<{ title: string; text: string }> | null;
}

export interface SlideContent {
  slide_number: number;
  title?: string | null;
  content_summary: string;
  image_prompt: string;
  overlay_text?: string | null;
  speaker_notes?: string | null;
  layout_type: 'image-only' | 'split-left' | 'split-right' | 'panel' | 'overlay';
  text_content?: TextContent | null;
  infographic_style: boolean;
}

export interface DeckStructure {
  deck_title: string;
  slides: SlideContent[];
  total_slides: number;
}

export interface ClarificationQuestion {
  question_id: number;
  category: 'structure' | 'style' | 'brand' | 'content';
  question: string;
  options?: string[] | null;
  required: boolean;
}

export interface ClarificationResponse {
  question_id: number;
  answer: string;
}

export interface BrandAssets {
  reference_images: string[];
  style_description?: string | null;
}

export type TextMode = 'minimal' | 'rich';

export interface WizardState {
  step: number;
  sessionId: string | null;
  mode: TextMode | null;
  contentFile: File | null;
  brandAssets: File[];
  deckStructure: DeckStructure | null;
  clarificationQuestions: ClarificationQuestion[];
  clarificationResponses: ClarificationResponse[];
  jobId: string | null;
  outputPath: string | null;
}

export interface ProgressUpdate {
  type: 'progress';
  event: 'parsing_started' | 'parsing_completed' | 'image_generation_started' |
         'image_generated' | 'image_generation_completed' | 'assembly_started' |
         'assembly_completed' | 'error';
  data: {
    slide_number?: number;
    completed?: number;
    total?: number;
    percentage?: number;
    message?: string;
    error?: string;
  };
}

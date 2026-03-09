import axios, { AxiosInstance } from 'axios';
import type {
  UploadFileResponse,
  ParseContentResponse,
  ParseContentRequest,
  RefineStructureRequest,
  RefineStructureResponse,
  StartGenerationRequest,
  StartGenerationResponse,
  GenerationStatusResponse,
} from '@/types/api';

class APIClient {
  private client: AxiosInstance;

  constructor(baseURL: string = '') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 120000,
    });
  }

  // File Upload
  async uploadContentFile(file: File): Promise<UploadFileResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<UploadFileResponse>(
      '/api/files/content',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async uploadBrandAssets(files: File[]): Promise<UploadFileResponse[]> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await this.client.post<UploadFileResponse[]>(
      '/api/files/brand-assets',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  // Generation Workflow
  async parseContent(request: ParseContentRequest): Promise<ParseContentResponse> {
    const response = await this.client.post<ParseContentResponse>(
      '/api/generation/parse',
      request
    );
    return response.data;
  }

  async refineStructure(request: RefineStructureRequest): Promise<RefineStructureResponse> {
    const response = await this.client.post<RefineStructureResponse>(
      '/api/generation/refine',
      request
    );
    return response.data;
  }

  async startGeneration(request: StartGenerationRequest): Promise<StartGenerationResponse> {
    const response = await this.client.post<StartGenerationResponse>(
      '/api/generation/start',
      request
    );
    return response.data;
  }

  async getGenerationStatus(jobId: string): Promise<GenerationStatusResponse> {
    const response = await this.client.get<GenerationStatusResponse>(
      `/api/generation/status/${jobId}`
    );
    return response.data;
  }

  async downloadPresentation(jobId: string): Promise<Blob> {
    const response = await this.client.get(`/api/generation/download/${jobId}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Health Check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/api/health');
    return response.data;
  }
}

export const apiClient = new APIClient();

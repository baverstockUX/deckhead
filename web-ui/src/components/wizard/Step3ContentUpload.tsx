import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileUpload } from '@/components/shared/FileUpload';
import { useWizard } from '@/hooks/useWizardState';
import { apiClient } from '@/services/api';

export function Step3ContentUpload() {
  const { state, setContentFile, nextStep, prevStep } = useWizard();
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFilesSelected = async (files: File[]) => {
    if (files.length === 0) return;

    const file = files[0];
    setContentFile(file);
    setError(null);

    // Upload file to backend
    try {
      setIsUploading(true);
      await apiClient.uploadContentFile(file);
      setIsUploading(false);
    } catch (err) {
      setError('Failed to upload file. Please try again.');
      setIsUploading(false);
      console.error('Upload error:', err);
    }
  };

  const handleRemoveFile = () => {
    setContentFile(null);
    setError(null);
  };

  const handleContinue = () => {
    if (state.contentFile) {
      nextStep();
    }
  };

  return (
    <Card variant="glass" className="mx-auto">
      <CardHeader>
        <CardTitle>Upload Your Content</CardTitle>
        <CardDescription>
          Upload a Markdown or text file containing your presentation content
        </CardDescription>
      </CardHeader>

      <CardContent>
        <FileUpload
          accept={['.md', '.txt', '.markdown']}
          multiple={false}
          maxSize={10 * 1024 * 1024}
          onFilesSelected={handleFilesSelected}
          currentFiles={state.contentFile ? [state.contentFile] : []}
          onRemoveFile={handleRemoveFile}
        />

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        <div className="mt-6 p-6 bg-slate-50 rounded-2xl border border-slate-200">
          <h4 className="font-semibold text-slate-900 mb-3">Content Format Tips</h4>
          <ul className="space-y-2 text-sm text-slate-600">
            <li className="flex items-start gap-2">
              <span className="text-primary-500 mt-0.5">•</span>
              <span>Use Markdown headings (#, ##) to structure your content</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary-500 mt-0.5">•</span>
              <span>Each section will be analyzed for slide generation</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary-500 mt-0.5">•</span>
              <span>Include bullet points for key takeaways (Rich mode)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary-500 mt-0.5">•</span>
              <span>Add statistics and data for visual impact</span>
            </li>
          </ul>
        </div>
      </CardContent>

      <CardFooter>
        <Button variant="outline" onClick={prevStep}>
          Back
        </Button>
        <Button
          onClick={handleContinue}
          disabled={!state.contentFile || isUploading}
          isLoading={isUploading}
        >
          Continue
        </Button>
      </CardFooter>
    </Card>
  );
}

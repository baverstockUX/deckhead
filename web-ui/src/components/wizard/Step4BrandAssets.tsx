import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileUpload } from '@/components/shared/FileUpload';
import { useWizard } from '@/hooks/useWizardState';
import { apiClient } from '@/services/api';

export function Step4BrandAssets() {
  const { state, setBrandAssets, removeBrandAsset, nextStep, prevStep } = useWizard();
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFilesSelected = async (files: File[]) => {
    if (files.length === 0) return;

    setBrandAssets([...state.brandAssets, ...files]);
    setError(null);

    // Upload files to backend
    try {
      setIsUploading(true);
      await apiClient.uploadBrandAssets(files);
      setIsUploading(false);
    } catch (err) {
      setError('Failed to upload brand assets. Please try again.');
      setIsUploading(false);
      console.error('Upload error:', err);
    }
  };

  const handleSkip = () => {
    nextStep();
  };

  const handleContinue = () => {
    nextStep();
  };

  return (
    <Card variant="glass" className="mx-auto">
      <CardHeader>
        <CardTitle>Brand Assets (Optional)</CardTitle>
        <CardDescription>
          Upload reference images to maintain consistent brand styling in generated images
        </CardDescription>
      </CardHeader>

      <CardContent>
        <FileUpload
          accept={['.jpg', '.jpeg', '.png', '.webp']}
          multiple={true}
          maxSize={50 * 1024 * 1024}
          onFilesSelected={handleFilesSelected}
          currentFiles={state.brandAssets}
          onRemoveFile={removeBrandAsset}
        />

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-6 p-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl border border-purple-200"
        >
          <h4 className="font-semibold text-slate-900 mb-3">Why Brand Assets?</h4>
          <p className="text-sm text-slate-600 leading-relaxed">
            Reference images help the AI understand your brand's visual style, color palette, and aesthetic.
            The generated images will be influenced by these references to maintain brand consistency.
          </p>
        </motion.div>
      </CardContent>

      <CardFooter>
        <Button variant="outline" onClick={prevStep}>
          Back
        </Button>
        <div className="flex gap-3">
          <Button variant="ghost" onClick={handleSkip}>
            Skip
          </Button>
          <Button
            onClick={handleContinue}
            disabled={isUploading}
            isLoading={isUploading}
          >
            Continue
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}

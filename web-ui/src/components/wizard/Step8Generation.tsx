import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, CheckCircle, Sparkles, Image as ImageIcon, FileDown } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Progress, CircularProgress } from '@/components/ui/Progress';
import { useWizard } from '@/hooks/useWizardState';
import { useWebSocket } from '@/hooks/useWebSocket';
import { apiClient } from '@/services/api';
import { downloadBlob } from '@/lib/utils';
import type { ProgressUpdate } from '@/types/models';

export function Step8Generation() {
  const { state, setJobId, setOutputPath, reset } = useWizard();
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<string>('Initializing...');
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  const handleWebSocketMessage = (data: ProgressUpdate) => {
    if (data.event === 'image_generated' && data.data.percentage) {
      setProgress(data.data.percentage);
      setStatus(data.data.message || 'Generating images...');
    } else if (data.event === 'image_generation_completed') {
      setProgress(100);
      setStatus('Assembling presentation...');
    } else if (data.event === 'assembly_completed') {
      setIsComplete(true);
      setStatus('Complete!');
      if (data.data.message) {
        setOutputPath(data.data.message);
      }
    } else if (data.event === 'error') {
      setError(data.data.error || 'An error occurred');
      setStatus('Error');
    }
  };

  const { isConnected, error: wsError } = useWebSocket(state.sessionId, {
    onMessage: handleWebSocketMessage,
  });

  useEffect(() => {
    const startGeneration = async () => {
      if (!state.sessionId) {
        setError('Session not found');
        return;
      }

      try {
        setStatus('Starting generation...');
        const response = await apiClient.startGeneration({
          session_id: state.sessionId,
        });

        setJobId(response.job_id);
        setStatus(response.message || 'Generating images...');
      } catch (err) {
        console.error('Generation error:', err);
        setError('Failed to start generation. Please try again.');
      }
    };

    startGeneration();
  }, [state.sessionId, setJobId]);

  const handleDownload = async () => {
    if (!state.jobId) return;

    try {
      setIsDownloading(true);
      const blob = await apiClient.downloadPresentation(state.jobId);
      const filename = `${state.deckStructure?.deck_title.replace(/\s+/g, '_') || 'presentation'}.pptx`;
      downloadBlob(blob, filename);
      setIsDownloading(false);
    } catch (err) {
      console.error('Download error:', err);
      setError('Failed to download presentation');
      setIsDownloading(false);
    }
  };

  const handleStartNew = () => {
    reset();
  };

  return (
    <Card variant="glass" className="text-center mx-auto">
      <CardHeader>
        <CardTitle>
          {isComplete ? 'Your Presentation is Ready!' : 'Generating Your Presentation'}
        </CardTitle>
        <CardDescription>
          {isComplete
            ? 'Download your PowerPoint presentation'
            : 'Creating beautiful slides with AI-generated images'}
        </CardDescription>
      </CardHeader>

      <CardContent>
        <div className="flex flex-col items-center justify-center py-8 space-y-8">
          <AnimatePresence mode="wait">
            {isComplete ? (
              <motion.div
                key="complete"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                exit={{ scale: 0 }}
                transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                className="relative"
              >
                <div className="p-8 rounded-full bg-gradient-to-br from-emerald-500 to-green-500 shadow-strong">
                  <CheckCircle className="w-16 h-16 text-white" />
                </div>
                <motion.div
                  className="absolute inset-0 rounded-full border-4 border-emerald-300"
                  animate={{ scale: [1, 1.3, 1], opacity: [0.7, 0, 0.7] }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'easeOut' }}
                />
              </motion.div>
            ) : (
              <motion.div
                key="progress"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <CircularProgress value={progress} size={140} strokeWidth={10} />
              </motion.div>
            )}
          </AnimatePresence>

          <div className="space-y-4 w-full max-w-md">
            <motion.div
              key={status}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-2"
            >
              <p className="text-lg font-medium text-slate-900">{status}</p>
              {!isComplete && !error && (
                <p className="text-sm text-slate-500">
                  {isConnected ? 'Connected to server' : 'Connecting...'}
                </p>
              )}
            </motion.div>

            {!isComplete && !error && (
              <Progress value={progress} showLabel={false} className="w-full" />
            )}

            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-4 bg-red-50 border border-red-200 rounded-xl"
              >
                <p className="text-sm text-red-700">{error}</p>
              </motion.div>
            )}

            {wsError && !isConnected && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-4 bg-amber-50 border border-amber-200 rounded-xl"
              >
                <p className="text-sm text-amber-700">
                  Connection issue. Updates may be delayed.
                </p>
              </motion.div>
            )}
          </div>

          {!isComplete && !error && state.deckStructure && (
            <div className="grid grid-cols-3 gap-4 w-full max-w-md pt-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="p-4 bg-white/80 backdrop-blur-sm rounded-xl border border-slate-200 text-center"
              >
                <ImageIcon className="w-6 h-6 text-primary-600 mx-auto mb-2" />
                <p className="text-xs text-slate-600">Images</p>
                <p className="text-lg font-semibold text-slate-900">
                  {Math.round((progress / 100) * state.deckStructure.total_slides)}
                  <span className="text-sm text-slate-500">
                    /{state.deckStructure.total_slides}
                  </span>
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="p-4 bg-white/80 backdrop-blur-sm rounded-xl border border-slate-200 text-center"
              >
                <Sparkles className="w-6 h-6 text-secondary-600 mx-auto mb-2" />
                <p className="text-xs text-slate-600">Quality</p>
                <p className="text-lg font-semibold text-slate-900">AI</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="p-4 bg-white/80 backdrop-blur-sm rounded-xl border border-slate-200 text-center"
              >
                <FileDown className="w-6 h-6 text-emerald-600 mx-auto mb-2" />
                <p className="text-xs text-slate-600">Format</p>
                <p className="text-lg font-semibold text-slate-900">PPTX</p>
              </motion.div>
            </div>
          )}
        </div>
      </CardContent>

      {isComplete && (
        <CardFooter className="justify-center gap-4">
          <Button
            variant="outline"
            size="lg"
            onClick={handleStartNew}
          >
            Create Another
          </Button>
          <Button
            size="lg"
            onClick={handleDownload}
            isLoading={isDownloading}
            className="min-w-[200px]"
          >
            <Download className="w-5 h-5 mr-2" />
            Download Presentation
          </Button>
        </CardFooter>
      )}
    </Card>
  );
}

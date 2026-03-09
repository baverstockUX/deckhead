import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2, Sparkles } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { useWizard } from '@/hooks/useWizardState';
import { apiClient } from '@/services/api';

export function Step5Parsing() {
  const { state, setDeckStructure, setClarificationQuestions, nextStep } = useWizard();
  const [status, setStatus] = useState<string>('Initializing...');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const parseContent = async () => {
      if (!state.contentFile || !state.mode) {
        setError('Missing required data');
        return;
      }

      try {
        setStatus('Reading your content...');

        // Read file content
        const content = await state.contentFile.text();

        setStatus('Analyzing structure with AI...');

        // Parse content
        const response = await apiClient.parseContent({
          content,
          mode: state.mode,
        });

        setStatus('Processing results...');

        // Store results
        setDeckStructure(response.deck_structure);
        setClarificationQuestions(response.clarification_questions);

        // Move to next step
        setTimeout(() => {
          nextStep();
        }, 500);
      } catch (err) {
        console.error('Parsing error:', err);
        setError('Failed to parse content. Please try again.');
        setStatus('Error occurred');
      }
    };

    parseContent();
  }, [state.contentFile, state.mode, setDeckStructure, setClarificationQuestions, nextStep]);

  return (
    <Card variant="glass" className="text-center mx-auto">
      <CardHeader>
        <CardTitle>Analyzing Your Content</CardTitle>
        <CardDescription>
          Our AI is parsing your content and structuring your presentation
        </CardDescription>
      </CardHeader>

      <CardContent>
        <div className="flex flex-col items-center justify-center py-12 space-y-8">
          <motion.div
            animate={{
              rotate: 360,
              scale: [1, 1.1, 1],
            }}
            transition={{
              rotate: { duration: 2, repeat: Infinity, ease: 'linear' },
              scale: { duration: 1, repeat: Infinity, ease: 'easeInOut' },
            }}
            className="relative"
          >
            <div className="p-8 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 shadow-strong">
              <Sparkles className="w-12 h-12 text-white" />
            </div>
            <motion.div
              className="absolute inset-0 rounded-full border-4 border-primary-300"
              animate={{ scale: [1, 1.3, 1], opacity: [0.7, 0, 0.7] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeOut' }}
            />
          </motion.div>

          <div className="space-y-3">
            <motion.div
              key={status}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-center gap-3"
            >
              <Loader2 className="w-5 h-5 animate-spin text-primary-600" />
              <p className="text-lg font-medium text-slate-900">{status}</p>
            </motion.div>

            {error ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-4 bg-red-50 border border-red-200 rounded-xl"
              >
                <p className="text-sm text-red-700">{error}</p>
              </motion.div>
            ) : (
              <p className="text-sm text-slate-500">
                This may take a few moments depending on content length
              </p>
            )}
          </div>

          <div className="grid grid-cols-3 gap-4 w-full max-w-md">
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="h-2 bg-gradient-to-r from-primary-200 to-secondary-200 rounded-full overflow-hidden"
              >
                <motion.div
                  className="h-full bg-gradient-to-r from-primary-500 to-secondary-500"
                  animate={{ x: ['-100%', '200%'] }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: 'easeInOut',
                    delay: i * 0.2,
                  }}
                />
              </motion.div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

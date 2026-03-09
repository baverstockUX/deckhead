import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HelpCircle, CheckCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useWizard } from '@/hooks/useWizardState';
import { apiClient } from '@/services/api';
import { cn } from '@/lib/utils';

const categoryColors = {
  structure: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300' },
  style: { bg: 'bg-purple-100', text: 'text-purple-700', border: 'border-purple-300' },
  brand: { bg: 'bg-amber-100', text: 'text-amber-700', border: 'border-amber-300' },
  content: { bg: 'bg-emerald-100', text: 'text-emerald-700', border: 'border-emerald-300' },
};

export function Step6Clarifications() {
  const { state, updateClarificationResponse, setDeckStructure, nextStep, prevStep } = useWizard();
  const [isRefining, setIsRefining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnswerChange = (questionId: number, answer: string) => {
    updateClarificationResponse(questionId, answer);
  };

  const handleSkip = () => {
    nextStep();
  };

  const handleSubmit = async () => {
    if (!state.deckStructure) {
      setError('Missing deck structure');
      return;
    }

    try {
      setIsRefining(true);
      setError(null);

      const response = await apiClient.refineStructure({
        deck_structure: state.deckStructure,
        clarifications: state.clarificationResponses,
        mode: state.mode || 'minimal',
      });

      setDeckStructure(response.deck_structure);
      setIsRefining(false);
      nextStep();
    } catch (err) {
      console.error('Refinement error:', err);
      setError('Failed to refine structure. Please try again.');
      setIsRefining(false);
    }
  };

  if (!state.clarificationQuestions || state.clarificationQuestions.length === 0) {
    // No questions, skip this step
    setTimeout(() => nextStep(), 100);
    return null;
  }

  return (
    <Card variant="glass" className="mx-auto">
      <CardHeader>
        <CardTitle>Clarification Questions</CardTitle>
        <CardDescription>
          Help us refine your presentation by answering a few questions
        </CardDescription>
      </CardHeader>

      <CardContent>
        <div className="space-y-6">
          <AnimatePresence>
            {state.clarificationQuestions.map((question, index) => {
              const colors = categoryColors[question.category];
              const currentAnswer = state.clarificationResponses.find(
                (r) => r.question_id === question.question_id
              )?.answer;

              return (
                <motion.div
                  key={question.question_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-6 bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-200 shadow-sm"
                >
                  <div className="flex items-start gap-4 mb-4">
                    <div className={cn('p-2 rounded-xl', colors.bg)}>
                      <HelpCircle className={cn('w-5 h-5', colors.text)} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span
                          className={cn(
                            'text-xs font-medium px-2 py-1 rounded-full',
                            colors.bg,
                            colors.text
                          )}
                        >
                          {question.category.toUpperCase()}
                        </span>
                        {question.required && (
                          <span className="text-xs text-red-500">* Required</span>
                        )}
                      </div>
                      <p className="text-slate-900 font-medium">{question.question}</p>
                    </div>
                  </div>

                  {question.options && question.options.length > 0 ? (
                    <div className="space-y-2">
                      {question.options.map((option, optIndex) => (
                        <motion.button
                          key={optIndex}
                          whileHover={{ scale: 1.01 }}
                          whileTap={{ scale: 0.99 }}
                          onClick={() => handleAnswerChange(question.question_id, option)}
                          className={cn(
                            'w-full p-4 rounded-xl text-left transition-all border-2',
                            currentAnswer === option
                              ? 'border-primary-500 bg-primary-50 shadow-md'
                              : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm'
                          )}
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-slate-900">{option}</span>
                            {currentAnswer === option && (
                              <CheckCircle className="w-5 h-5 text-primary-600" />
                            )}
                          </div>
                        </motion.button>
                      ))}
                    </div>
                  ) : (
                    <input
                      type="text"
                      value={currentAnswer || ''}
                      onChange={(e) =>
                        handleAnswerChange(question.question_id, e.target.value)
                      }
                      placeholder="Type your answer..."
                      className="w-full p-4 rounded-xl border-2 border-slate-200 focus:border-primary-500 focus:outline-none transition-colors"
                    />
                  )}
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl"
          >
            <p className="text-sm text-red-700">{error}</p>
          </motion.div>
        )}
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
            onClick={handleSubmit}
            disabled={isRefining}
            isLoading={isRefining}
          >
            {state.clarificationResponses.length > 0 ? 'Submit & Refine' : 'Continue'}
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}

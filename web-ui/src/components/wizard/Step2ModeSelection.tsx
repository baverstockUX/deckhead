import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ImageIcon, FileText, Check } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useWizard } from '@/hooks/useWizardState';
import { cn } from '@/lib/utils';
import type { TextMode } from '@/types/models';

export function Step2ModeSelection() {
  const { state, setMode, nextStep, prevStep } = useWizard();
  const [selectedMode, setSelectedMode] = useState<TextMode | null>(state.mode);

  const modes = [
    {
      id: 'minimal' as TextMode,
      icon: ImageIcon,
      title: 'Minimal Mode',
      description: 'Titles only, clean visual storytelling',
      details: 'Perfect for executive summaries and pitch decks. All slides use full-bleed images with integrated titles.',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      id: 'rich' as TextMode,
      icon: FileText,
      title: 'Rich Mode',
      description: 'Full text content with bullets, statistics, and callouts',
      details: 'Ideal for educational content and detailed proposals. Includes structured text content rendered in images.',
      color: 'from-purple-500 to-pink-500',
    },
  ];

  const handleContinue = () => {
    if (selectedMode) {
      setMode(selectedMode);
      nextStep();
    }
  };

  return (
    <Card variant="glass" className="mx-auto">
      <CardHeader>
        <CardTitle>Choose Your Presentation Style</CardTitle>
        <CardDescription>
          Select how you want your text content to be displayed
        </CardDescription>
      </CardHeader>

      <CardContent>
        <div className="grid md:grid-cols-2 gap-6">
          {modes.map((mode) => (
            <motion.div
              key={mode.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setSelectedMode(mode.id)}
              className={cn(
                'relative p-6 rounded-2xl border-2 cursor-pointer transition-all',
                selectedMode === mode.id
                  ? 'border-primary-500 bg-primary-50/50 shadow-strong'
                  : 'border-slate-200 bg-white/80 hover:border-slate-300 hover:shadow-md'
              )}
            >
              {selectedMode === mode.id && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute top-4 right-4 p-1.5 bg-primary-500 rounded-full"
                >
                  <Check className="w-4 h-4 text-white" />
                </motion.div>
              )}

              <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-br ${mode.color} mb-4`}>
                <mode.icon className="w-8 h-8 text-white" />
              </div>

              <h3 className="text-xl font-semibold text-slate-900 mb-2">{mode.title}</h3>
              <p className="text-slate-600 mb-3">{mode.description}</p>
              <p className="text-sm text-slate-500 leading-relaxed">{mode.details}</p>
            </motion.div>
          ))}
        </div>

        {selectedMode && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-6 p-4 bg-primary-50 border border-primary-200 rounded-xl"
          >
            <p className="text-sm text-primary-900">
              <strong>Selected:</strong>{' '}
              {modes.find((m) => m.id === selectedMode)?.title}
            </p>
          </motion.div>
        )}
      </CardContent>

      <CardFooter>
        <Button variant="outline" onClick={prevStep}>
          Back
        </Button>
        <Button onClick={handleContinue} disabled={!selectedMode}>
          Continue
        </Button>
      </CardFooter>
    </Card>
  );
}

import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Zap, Image as ImageIcon } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useWizard } from '@/hooks/useWizardState';

export function Step1Welcome() {
  const { nextStep } = useWizard();

  const features = [
    {
      icon: Sparkles,
      title: 'AI-Powered Content',
      description: 'Intelligent parsing and structuring of your content',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: ImageIcon,
      title: 'Beautiful Imagery',
      description: 'Generate stunning images with Google Gemini',
      color: 'from-purple-500 to-pink-500',
    },
    {
      icon: Zap,
      title: 'Fast Generation',
      description: 'Parallel image generation for quick results',
      color: 'from-amber-500 to-orange-500',
    },
  ];

  return (
    <Card variant="glass" className="max-w-3xl mx-auto">
      <CardHeader className="text-center pb-3">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mb-3"
        >
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500 shadow-strong mb-2">
            <Sparkles className="w-7 h-7 text-white" />
          </div>
        </motion.div>

        <CardTitle className="text-2xl md:text-3xl bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
          Welcome to Deckhead
        </CardTitle>
        <CardDescription className="text-base">
          Transform your content into stunning PowerPoint presentations with AI
        </CardDescription>
      </CardHeader>

      <CardContent className="py-4">
        <div className="grid md:grid-cols-3 gap-4 mb-4">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 + index * 0.1 }}
              className="relative group"
            >
              <div className="p-4 bg-white/80 backdrop-blur-sm rounded-xl border border-slate-200 hover:border-slate-300 transition-all hover:shadow-md">
                <div className={`inline-flex p-2 rounded-lg bg-gradient-to-br ${feature.color} mb-2`}>
                  <feature.icon className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-semibold text-sm text-slate-900 mb-1">{feature.title}</h3>
                <p className="text-xs text-slate-600">{feature.description}</p>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="p-4 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl border border-primary-200"
        >
          <p className="text-center text-sm text-slate-700 leading-relaxed">
            In just a few simple steps, you'll have a professional presentation ready to download.
            Let's get started!
          </p>
        </motion.div>
      </CardContent>

      <CardFooter className="justify-center pt-3">
        <Button
          size="lg"
          onClick={nextStep}
          className="min-w-[200px]"
        >
          Get Started
        </Button>
      </CardFooter>
    </Card>
  );
}

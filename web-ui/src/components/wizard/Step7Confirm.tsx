import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Image as ImageIcon, Layout } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useWizard } from '@/hooks/useWizardState';

export function Step7Confirm() {
  const { state, nextStep, prevStep } = useWizard();

  if (!state.deckStructure) {
    return (
      <Card variant="glass" className="mx-auto">
        <CardContent>
          <p className="text-center text-slate-600">No deck structure available</p>
        </CardContent>
      </Card>
    );
  }

  const { deck_title, slides, total_slides } = state.deckStructure;

  return (
    <Card variant="glass" className="mx-auto">
      <CardHeader>
        <CardTitle>Confirm Your Presentation</CardTitle>
        <CardDescription>
          Review the structure before we generate your slides
        </CardDescription>
      </CardHeader>

      <CardContent>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-6"
        >
          {/* Deck Overview */}
          <div className="p-6 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-2xl border border-primary-200">
            <div className="grid md:grid-cols-3 gap-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-primary-100 rounded-xl">
                  <FileText className="w-6 h-6 text-primary-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-600">Presentation</p>
                  <p className="font-semibold text-slate-900">{deck_title}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-secondary-100 rounded-xl">
                  <Layout className="w-6 h-6 text-secondary-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-600">Total Slides</p>
                  <p className="font-semibold text-slate-900">{total_slides}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-100 rounded-xl">
                  <ImageIcon className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-600">Mode</p>
                  <p className="font-semibold text-slate-900 capitalize">{state.mode}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Slides Table */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-200 overflow-hidden">
            <div className="max-h-96 overflow-y-auto">
              <table className="w-full">
                <thead className="bg-slate-50 sticky top-0">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-700 uppercase">
                      Slide
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-700 uppercase">
                      Title
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-700 uppercase">
                      Content Summary
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-700 uppercase">
                      Layout
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {slides.map((slide, index) => (
                    <motion.tr
                      key={slide.slide_number}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="hover:bg-slate-50 transition-colors"
                    >
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-700 text-sm font-semibold">
                          {slide.slide_number}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <p className="font-medium text-slate-900">
                          {slide.title || '(Untitled)'}
                        </p>
                      </td>
                      <td className="px-6 py-4">
                        <p className="text-sm text-slate-600 line-clamp-2">
                          {slide.content_summary}
                        </p>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
                          {slide.layout_type}
                        </span>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
            <p className="text-sm text-blue-900">
              <strong>Ready to generate?</strong> This will create {total_slides} images and assemble
              your PowerPoint presentation. The process typically takes a few minutes.
            </p>
          </div>
        </motion.div>
      </CardContent>

      <CardFooter>
        <Button variant="outline" onClick={prevStep}>
          Back
        </Button>
        <Button size="lg" onClick={nextStep}>
          Generate Presentation
        </Button>
      </CardFooter>
    </Card>
  );
}

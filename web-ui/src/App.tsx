import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { WizardProvider, useWizard } from '@/hooks/useWizardState';
import { Step1Welcome } from '@/components/wizard/Step1Welcome';
import { Step2ModeSelection } from '@/components/wizard/Step2ModeSelection';
import { Step3ContentUpload } from '@/components/wizard/Step3ContentUpload';
import { Step4BrandAssets } from '@/components/wizard/Step4BrandAssets';
import { Step5Parsing } from '@/components/wizard/Step5Parsing';
import { Step6Clarifications } from '@/components/wizard/Step6Clarifications';
import { Step7Confirm } from '@/components/wizard/Step7Confirm';
import { Step8Generation } from '@/components/wizard/Step8Generation';

function WizardBreadcrumb() {
  const { state } = useWizard();

  const steps = [
    { number: 1, label: 'Welcome' },
    { number: 2, label: 'Mode' },
    { number: 3, label: 'Content' },
    { number: 4, label: 'Brand Assets' },
    { number: 5, label: 'Parsing' },
    { number: 6, label: 'Questions' },
    { number: 7, label: 'Confirm' },
    { number: 8, label: 'Generate' },
  ];

  return (
    <div className="mb-4">
      <div className="flex items-center justify-center gap-1.5 flex-wrap">
        {steps.map((step, index) => (
          <React.Fragment key={step.number}>
            <div className="flex items-center gap-1.5">
              <motion.div
                className={`flex items-center justify-center w-8 h-8 rounded-full font-semibold text-xs transition-all ${
                  state.step === step.number
                    ? 'bg-gradient-to-br from-primary-500 to-secondary-500 text-white shadow-lg scale-110'
                    : state.step > step.number
                    ? 'bg-emerald-500 text-white'
                    : 'bg-slate-200 text-slate-500'
                }`}
                animate={{
                  scale: state.step === step.number ? 1.1 : 1,
                }}
                transition={{ duration: 0.3 }}
              >
                {step.number}
              </motion.div>
              <span
                className={`text-xs font-medium hidden sm:inline ${
                  state.step === step.number
                    ? 'text-slate-900'
                    : 'text-slate-500'
                }`}
              >
                {step.label}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div className="w-4 h-0.5 bg-slate-200 hidden md:block" />
            )}
          </React.Fragment>
        ))}
      </div>

      <motion.div
        className="mt-2 text-center"
        key={state.step}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <p className="text-xs text-slate-600">
          Step {state.step} of 8
        </p>
      </motion.div>
    </div>
  );
}

function WizardContent() {
  const { state } = useWizard();

  const renderStep = () => {
    switch (state.step) {
      case 1:
        return <Step1Welcome />;
      case 2:
        return <Step2ModeSelection />;
      case 3:
        return <Step3ContentUpload />;
      case 4:
        return <Step4BrandAssets />;
      case 5:
        return <Step5Parsing />;
      case 6:
        return <Step6Clarifications />;
      case 7:
        return <Step7Confirm />;
      case 8:
        return <Step8Generation />;
      default:
        return <Step1Welcome />;
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto flex justify-center">
      <AnimatePresence mode="wait">
        <motion.div
          key={state.step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
          className="w-full"
        >
          {renderStep()}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

function AppContent() {
  return (
    <div className="min-h-screen py-4 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-4"
        >
          <div className="inline-flex items-center gap-2 mb-2">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center shadow-lg">
              <span className="text-xl font-bold text-white">D</span>
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
              Deckhead
            </h1>
          </div>
          <p className="text-sm text-slate-600">AI-Powered PowerPoint Generator</p>
        </motion.div>

        {/* Breadcrumb */}
        <WizardBreadcrumb />

        {/* Wizard Content */}
        <WizardContent />

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-4 text-center text-xs text-slate-500"
        >
          <p>Powered by Google Gemini</p>
        </motion.footer>
      </div>
    </div>
  );
}

function App() {
  return (
    <WizardProvider>
      <AppContent />
    </WizardProvider>
  );
}

export default App;

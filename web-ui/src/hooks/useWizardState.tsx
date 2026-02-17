import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import type {
  WizardState,
  TextMode,
  DeckStructure,
  ClarificationQuestion,
  ClarificationResponse,
} from '@/types/models';

interface WizardContextType {
  state: WizardState;
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  setSessionId: (sessionId: string) => void;
  setMode: (mode: TextMode) => void;
  setContentFile: (file: File | null) => void;
  setBrandAssets: (files: File[]) => void;
  addBrandAsset: (file: File) => void;
  removeBrandAsset: (index: number) => void;
  setDeckStructure: (structure: DeckStructure | null) => void;
  setClarificationQuestions: (questions: ClarificationQuestion[]) => void;
  addClarificationResponse: (response: ClarificationResponse) => void;
  updateClarificationResponse: (questionId: number, answer: string) => void;
  setJobId: (jobId: string) => void;
  setOutputPath: (path: string) => void;
  reset: () => void;
}

const initialState: WizardState = {
  step: 1,
  sessionId: null,
  mode: null,
  contentFile: null,
  brandAssets: [],
  deckStructure: null,
  clarificationQuestions: [],
  clarificationResponses: [],
  jobId: null,
  outputPath: null,
};

const WizardContext = createContext<WizardContextType | undefined>(undefined);

export function WizardProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<WizardState>(initialState);

  const setStep = useCallback((step: number) => {
    setState((prev) => ({ ...prev, step }));
  }, []);

  const nextStep = useCallback(() => {
    setState((prev) => ({ ...prev, step: Math.min(prev.step + 1, 8) }));
  }, []);

  const prevStep = useCallback(() => {
    setState((prev) => ({ ...prev, step: Math.max(prev.step - 1, 1) }));
  }, []);

  const setSessionId = useCallback((sessionId: string) => {
    setState((prev) => ({ ...prev, sessionId }));
  }, []);

  const setMode = useCallback((mode: TextMode) => {
    setState((prev) => ({ ...prev, mode }));
  }, []);

  const setContentFile = useCallback((file: File | null) => {
    setState((prev) => ({ ...prev, contentFile: file }));
  }, []);

  const setBrandAssets = useCallback((files: File[]) => {
    setState((prev) => ({ ...prev, brandAssets: files }));
  }, []);

  const addBrandAsset = useCallback((file: File) => {
    setState((prev) => ({ ...prev, brandAssets: [...prev.brandAssets, file] }));
  }, []);

  const removeBrandAsset = useCallback((index: number) => {
    setState((prev) => ({
      ...prev,
      brandAssets: prev.brandAssets.filter((_, i) => i !== index),
    }));
  }, []);

  const setDeckStructure = useCallback((structure: DeckStructure | null) => {
    setState((prev) => ({ ...prev, deckStructure: structure }));
  }, []);

  const setClarificationQuestions = useCallback((questions: ClarificationQuestion[]) => {
    setState((prev) => ({ ...prev, clarificationQuestions: questions }));
  }, []);

  const addClarificationResponse = useCallback((response: ClarificationResponse) => {
    setState((prev) => ({
      ...prev,
      clarificationResponses: [...prev.clarificationResponses, response],
    }));
  }, []);

  const updateClarificationResponse = useCallback((questionId: number, answer: string) => {
    setState((prev) => {
      const existingIndex = prev.clarificationResponses.findIndex(
        (r) => r.question_id === questionId
      );

      if (existingIndex !== -1) {
        const updated = [...prev.clarificationResponses];
        updated[existingIndex] = { question_id: questionId, answer };
        return { ...prev, clarificationResponses: updated };
      } else {
        return {
          ...prev,
          clarificationResponses: [
            ...prev.clarificationResponses,
            { question_id: questionId, answer },
          ],
        };
      }
    });
  }, []);

  const setJobId = useCallback((jobId: string) => {
    setState((prev) => ({ ...prev, jobId }));
  }, []);

  const setOutputPath = useCallback((path: string) => {
    setState((prev) => ({ ...prev, outputPath: path }));
  }, []);

  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  const value: WizardContextType = {
    state,
    setStep,
    nextStep,
    prevStep,
    setSessionId,
    setMode,
    setContentFile,
    setBrandAssets,
    addBrandAsset,
    removeBrandAsset,
    setDeckStructure,
    setClarificationQuestions,
    addClarificationResponse,
    updateClarificationResponse,
    setJobId,
    setOutputPath,
    reset,
  };

  return <WizardContext.Provider value={value}>{children}</WizardContext.Provider>;
}

export function useWizard() {
  const context = useContext(WizardContext);
  if (context === undefined) {
    throw new Error('useWizard must be used within a WizardProvider');
  }
  return context;
}

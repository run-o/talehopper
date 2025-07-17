import React, { useState } from 'react';
import StoryForm from './components/StoryForm';
import StoryDisplay from './components/StoryDisplay';
import FeedbackModal from './components/FeedbackModal';
import { StoryPrompt } from './types/story';
import { generateStory, sendFeedback, FeedbackRequest } from './services/api';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './components/LanguageSwitcher';
import './App.css';


function App() {
  const { t } = useTranslation();
  const [storyPrompt, setStoryPrompt] = useState<StoryPrompt | null>(null);
  const [storyHistory, setStoryHistory] = useState<string[]>([]);
  const [storyChoices, setStoryChoices] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isStoryStarted, setIsStoryStarted] = useState<boolean>(false);
  const [lastChoice, setLastChoice] = useState<string | undefined>(undefined);
  const [lastUsedPrompt, setLastUsedPrompt] = useState<StoryPrompt | null>(null);
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState<boolean>(false);

  const handleStartStory = async (prompt: StoryPrompt) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await generateStory({
        prompt,
        history: [],
        choice: undefined,
      });
      
      setStoryPrompt(prompt);
      setLastUsedPrompt(prompt);
      setStoryHistory(response.history);
      setStoryChoices(response.choices);
      setIsStoryStarted(true);
      setLastChoice(undefined);
    } catch (err) {
      setError('Failed to start story. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChoiceSelected = async (choice: string) => {
    if (!storyPrompt) return;
    
    setIsLoading(true);
    setError(null);
    setLastChoice(choice);
    
    try {
      const response = await generateStory({
        prompt: storyPrompt,
        history: storyHistory,
        choice,
      });
      
      setStoryHistory(response.history);
      setStoryChoices(response.choices);
    } catch (err) {
      setError('Failed to continue story. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerateRequested = async () => {
    if (!storyPrompt || storyHistory.length === 0) return;
    
    setIsLoading(true);
    setError(null);
    
    // Remove the last paragraph from history
    const previousHistory = storyHistory.length > 1 
      ? storyHistory.slice(0, -1) 
      : [];
    
    try {
      // If this is the first paragraph, regenerate with empty history
      if (previousHistory.length === 0) {
        const response = await generateStory({
          prompt: storyPrompt,
          history: [],
          choice: undefined,
        });
        
        setStoryHistory(response.history);
        setStoryChoices(response.choices);
      } else {
        // Otherwise regenerate with the previous history and last choice
        const response = await generateStory({
          prompt: storyPrompt,
          history: previousHistory,
          choice: lastChoice,
        });
        
        setStoryHistory(response.history);
        setStoryChoices(response.choices);
      }
    } catch (err) {
      setError('Failed to regenerate story. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRestart = () => {
    setStoryPrompt(null);
    setStoryHistory([]);
    setStoryChoices([]);
    setIsStoryStarted(false);
    setError(null);
    setLastChoice(undefined);
    // We don't reset lastUsedPrompt here, so it can be used to prepopulate the form
  };

  const handleFeedbackSubmit = async (feedback: FeedbackRequest) => {
    await sendFeedback(feedback);
  };

  return (
    <div className="App">
      <div style={{ position: 'absolute', top: 20, right: 20 }}>
        <LanguageSwitcher />
      </div>
      <header className="App-header" style={{ display: 'flex', alignItems: 'center' }}>
        <img src="/talehopper_logo.png" alt="Tale Hopper Logo" className="App-logo" style={{ width: '200px', marginRight: '20px' }} />
        <div style={{ textAlign: 'center' }}>
          <h1>Tale Hopper</h1>
          <h2>{t('app.header')}</h2>
        </div>
      </header>
      <main>
        {!isStoryStarted ? (
          <StoryForm onSubmit={handleStartStory} isLoading={isLoading} initialPrompt={lastUsedPrompt || undefined} />
        ) : (
          <StoryDisplay 
            history={storyHistory}
            choices={storyChoices}
            onChoiceSelected={handleChoiceSelected}
            onRestart={handleRestart}
            onRegenerateRequested={handleRegenerateRequested}
            isLoading={isLoading}
            isStoryEnded={!!storyPrompt && storyHistory.length >= storyPrompt.length}
          />
        )}
        
        {error && <div className="error-message">{error}</div>}
      </main>
      
      <footer style={{ 
        position: 'fixed', 
        bottom: 20, 
        right: 20, 
        zIndex: 100 
      }}>
        <button
          onClick={() => setIsFeedbackModalOpen(true)}
          style={{
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '20px',
            padding: '10px 16px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
            transition: 'background-color 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#0056b3'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#007bff'}
        >
          {t('feedback.button')}
        </button>
      </footer>

      <FeedbackModal
        isOpen={isFeedbackModalOpen}
        onClose={() => setIsFeedbackModalOpen(false)}
        onSubmit={handleFeedbackSubmit}
      />
    </div>
  );
}

export default App;

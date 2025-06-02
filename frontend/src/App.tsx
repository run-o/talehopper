import React, { useState } from 'react';
import StoryForm from './components/StoryForm';
import StoryDisplay from './components/StoryDisplay';
import { StoryPrompt } from './types/story';
import { generateStory } from './services/api';
import './App.css';

function App() {
  const [storyPrompt, setStoryPrompt] = useState<StoryPrompt | null>(null);
  const [storyHistory, setStoryHistory] = useState<string[]>([]);
  const [storyChoices, setStoryChoices] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isStoryStarted, setIsStoryStarted] = useState<boolean>(false);
  const [lastChoice, setLastChoice] = useState<string | undefined>(undefined);

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
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Tale Hopper</h1>
        <p>Choose-Your-Own-Adventure Stories for Kids</p>
      </header>
      
      <main>
        {!isStoryStarted ? (
          <StoryForm onSubmit={handleStartStory} isLoading={isLoading} />
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
    </div>
  );
}

export default App;

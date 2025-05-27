import React from 'react';
import ParagraphList from './ParagraphList';
import ChoiceButtons from './ChoiceButtons';

interface StoryDisplayProps {
  history: string[];
  choices: string[];
  onChoiceSelected: (choice: string) => void;
  onRestart: () => void;
  isLoading: boolean;
}

const StoryDisplay: React.FC<StoryDisplayProps> = ({
  history,
  choices,
  onChoiceSelected,
  onRestart,
  isLoading,
}) => {
  return (
    <div className="story-display">
      <ParagraphList paragraphs={history} />
      
      <div className="story-controls">
        <ChoiceButtons 
          choices={choices} 
          onChoiceSelected={onChoiceSelected} 
          disabled={isLoading} 
        />
        
        <button 
          className="restart-button" 
          onClick={onRestart}
          disabled={isLoading}
        >
          Start a New Story
        </button>
      </div>
      
      {isLoading && <div className="loading-indicator">Loading next part of the story...</div>}
    </div>
  );
};

export default StoryDisplay;

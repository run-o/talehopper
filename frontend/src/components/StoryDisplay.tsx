import React from 'react';
import ParagraphList from './ParagraphList';
import ChoiceButtons from './ChoiceButtons';
import { useTranslation } from 'react-i18next';

interface StoryDisplayProps {
  history: string[];
  choices: string[];
  onChoiceSelected: (choice: string) => void;
  onRestart: () => void;
  onRegenerateRequested?: () => void;
  isLoading: boolean;
  isStoryEnded?: boolean;
}

const StoryDisplay: React.FC<StoryDisplayProps> = ({
  history,
  choices,
  onChoiceSelected,
  onRestart,
  onRegenerateRequested,
  isLoading,
  isStoryEnded = false,
}) => {
  const { t } = useTranslation();

  return (
    <div className="story-display">
      <ParagraphList 
        paragraphs={history} 
        onRegenerateRequested={onRegenerateRequested}
        isLoading={isLoading}
      />
      
      <div className="story-controls">
        <ChoiceButtons 
          choices={choices} 
          onChoiceSelected={onChoiceSelected} 
          disabled={isLoading}
          isStoryEnded={isStoryEnded}
        />
        
        <button 
          className="restart-button" 
          onClick={onRestart}
          disabled={isLoading}
        >
          {t('story_display.start')}
        </button>
      </div>
      
      {isLoading && <div className="loading-indicator">{t('story_display.loading')}</div>}
    </div>
  );
};

export default StoryDisplay;

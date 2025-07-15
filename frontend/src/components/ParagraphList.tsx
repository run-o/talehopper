import React from 'react';
import { useTranslation } from 'react-i18next';

interface ParagraphListProps {
  paragraphs: string[];
  onRegenerateRequested?: () => void;
  isLoading: boolean;
}

const ParagraphList: React.FC<ParagraphListProps> = ({ 
  paragraphs, 
  onRegenerateRequested,
  isLoading
}) => {
  const { t } = useTranslation();

  return (
    <div className="paragraph-list">
      {paragraphs.map((paragraph, index) => (
        <div key={index} className="story-paragraph">
          <p>{paragraph}</p>
          {index === paragraphs.length - 1 && onRegenerateRequested && (
            <button 
              className="regenerate-button" 
              onClick={onRegenerateRequested}
              disabled={isLoading}
            >
              {t('story_display.regenerate')}
            </button>
          )}
          {index < paragraphs.length - 1 && <hr />}
        </div>
      ))}
    </div>
  );
};

export default ParagraphList;

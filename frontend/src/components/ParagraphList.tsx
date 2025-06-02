import React from 'react';

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
              Regenerate last paragraph
            </button>
          )}
          {index < paragraphs.length - 1 && <hr />}
        </div>
      ))}
    </div>
  );
};

export default ParagraphList;

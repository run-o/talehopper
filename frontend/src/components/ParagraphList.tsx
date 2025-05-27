import React from 'react';

interface ParagraphListProps {
  paragraphs: string[];
}

const ParagraphList: React.FC<ParagraphListProps> = ({ paragraphs }) => {
  return (
    <div className="paragraph-list">
      {paragraphs.map((paragraph, index) => (
        <div key={index} className="story-paragraph">
          <p>{paragraph}</p>
          {index < paragraphs.length - 1 && <hr />}
        </div>
      ))}
    </div>
  );
};

export default ParagraphList;

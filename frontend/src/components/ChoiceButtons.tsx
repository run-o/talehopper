import React from 'react';

interface ChoiceButtonsProps {
  choices: string[];
  onChoiceSelected: (choice: string) => void;
  disabled: boolean;
  isStoryEnded?: boolean;
}

const ChoiceButtons: React.FC<ChoiceButtonsProps> = ({
  choices,
  onChoiceSelected,
  disabled,
  isStoryEnded = false,
}) => {
  return (
    <div className="choice-buttons">
      <h3>{isStoryEnded ? "The End." : "What happens next?"}</h3>
      <div className="buttons-container">
        {choices.map((choice, index) => (
          <button
            key={index}
            onClick={() => onChoiceSelected(choice)}
            disabled={disabled}
            className="choice-button"
          >
            {choice}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ChoiceButtons;

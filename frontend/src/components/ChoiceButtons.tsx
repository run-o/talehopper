import React from 'react';
import { useTranslation } from 'react-i18next';

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
  const { t } = useTranslation();

  return (
    <div className="choice-buttons">
      <h3>{isStoryEnded ? t('story_display.end') : t('story_display.next')}</h3>
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

import React, { useState } from 'react';
import { 
  StoryPrompt, 
  Character, 
  Gender, 
  Personality, 
  Tone, 
  ConflictType, 
  EndingStyle,
  GENDER_OPTIONS,
  PERSONALITY_OPTIONS,
  TONE_OPTIONS,
  CONFLICT_OPTIONS,
  ENDING_OPTIONS
} from '../types/story';
import { useTranslation } from 'react-i18next';
import DatalistInput from './DatalistInput';


interface StoryFormProps {
  onSubmit: (prompt: StoryPrompt) => void;
  isLoading: boolean;
  initialPrompt?: StoryPrompt;
}

const StoryForm: React.FC<StoryFormProps> = ({ onSubmit, isLoading, initialPrompt }) => {
  const { t } = useTranslation();
  const [age, setAge] = useState<number>(initialPrompt?.age || 8);
  const [language, setLanguage] = useState<"english" | "french">(initialPrompt?.language || "english");
  const [length, setLength] = useState<number>(initialPrompt?.length || 10);
  const [prompt, setPrompt] = useState<string>(initialPrompt?.prompt || "");
  const [environment, setEnvironment] = useState<string>(initialPrompt?.environment || "");
  const [theme, setTheme] = useState<string>(initialPrompt?.theme || "");
  const [tone, setTone] = useState<StoryPrompt["tone"]>(initialPrompt?.tone || undefined);
  const [conflictType, setConflictType] = useState<StoryPrompt["conflict_type"]>(initialPrompt?.conflict_type || undefined);
  const [endingStyle, setEndingStyle] = useState<StoryPrompt["ending_style"]>(initialPrompt?.ending_style || undefined);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState<boolean>(
    !!(initialPrompt?.theme || initialPrompt?.tone || initialPrompt?.conflict_type || initialPrompt?.ending_style)
  );
  
  // Character management
  const [characters, setCharacters] = useState<Character[]>(initialPrompt?.characters || []);
  const [characterName, setCharacterName] = useState<string>("");
  const [characterType, setCharacterType] = useState<string>("");
  const [characterGender, setCharacterGender] = useState<Character["gender"]>(undefined);
  const [characterPersonality, setCharacterPersonality] = useState<Character["personality"]>(undefined);

  const addCharacter = () => {
    if (characterName && characterType) {
      setCharacters([
        ...characters,
        {
          name: characterName,
          type: characterType,
          gender: characterGender || undefined,
          personality: characterPersonality || undefined,
        },
      ]);
      setCharacterName("");
      setCharacterType("");
      setCharacterGender(undefined);
      setCharacterPersonality(undefined);
    }
  };

  const removeCharacter = (index: number) => {
    setCharacters(characters.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const storyPrompt: StoryPrompt = {
      age,
      language,
      length,
      prompt: prompt || undefined,
      characters: characters.length > 0 ? characters : undefined,
      environment: environment || undefined,
      theme: theme || undefined,
      tone: tone || undefined,
      conflict_type: conflictType || undefined,
      ending_style: endingStyle || undefined,
    };
    
    onSubmit(storyPrompt);
  };

  return (
    <div className="story-form-container">
      <h2>{t('story_form.title')}</h2>
      <form onSubmit={handleSubmit} className="story-form">
        <div className="form-group">
            <label htmlFor="age">{t('story_form.age')}</label>
            <select
                id="age"
                value={age}
                onChange={(e) => setAge(Number(e.target.value))}
                required
            >
                {Array.from({ length: 12 }, (_, i) => i + 1).map((num) => (
                <option key={num} value={num}>
                    {num}
                </option>
                ))}
            </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="language">{t('story_form.language')}</label>
          <select
            id="language"
            value={language}
            onChange={(e) => setLanguage(e.target.value as "english" | "french")}
            required
          >
            <option value="english">{t('story_form.language_english')}</option>
            <option value="french">{t('story_form.language_french')}</option>
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="length">{t('story_form.length')}</label>
          <input
            type="number"
            id="length"
            min="1"
            max="60"
            value={length}
            onChange={(e) => setLength(Number(e.target.value))}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="prompt">{t('story_form.prompt')}</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={t('story_form.prompt_placeholder')}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="environment">{t('story_form.environment')}</label>
          <input
            type="text"
            id="environment"
            value={environment}
            onChange={(e) => setEnvironment(e.target.value)}
            placeholder={t('story_form.environment_placeholder')}
          />
        </div>
        
        <div className="form-group characters-section">
          <h3>{t('story_form.characters')}</h3>

          <div className="character-inputs">
            <input
              type="text"
              value={characterName}
              onChange={(e) => setCharacterName(e.target.value)}
              placeholder={t('story_form.character_name')}
            />
            <input
              type="text"
              value={characterType}
              onChange={(e) => setCharacterType(e.target.value)}
              placeholder={t('story_form.character_type')}
            />
            
            {/* Gender with Datalist */}
            <DatalistInput<Gender>
              id="characterGender"
              value={characterGender}
              onChange={setCharacterGender}
              placeholder={t('story_form.character_gender')}
              options={GENDER_OPTIONS}
              optionTranslationKey="options.gender"
            />

            {/* Personality with Datalist */}
            <DatalistInput<Personality>
              id="characterPersonality"
              value={characterPersonality}
              onChange={setCharacterPersonality}
              placeholder={t('story_form.character_personality')}
              options={PERSONALITY_OPTIONS}
              optionTranslationKey="options.personality"
            />

            <button
              type="button"
              onClick={addCharacter}
              disabled={!characterName || !characterType}
            >
              {t('story_form.add')}
            </button>
          </div>

            {characters.length > 0 && (
            <ul className="character-list">
              {characters.map((character, index) => (
              <li key={index}>
                {character.name} ({character.type}
                {character.gender ? `, ${character.gender}` : ""}
                {character.personality ? `, ${character.personality}` : ""})
                <button type="button" onClick={() => removeCharacter(index)}>{t('story_form.remove')}</button>
              </li>
              ))}
            </ul>
            )}
        </div>
        
        {/* Advanced Options Accordion */}
        <div className="accordion">
          <div 
            className={`accordion-header ${showAdvancedOptions ? 'expanded' : ''}`}
            onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
            role="button"
            tabIndex={0}
            aria-expanded={showAdvancedOptions}
            aria-controls="advanced-options"
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                setShowAdvancedOptions(!showAdvancedOptions);
              }
            }}
          >
            <h4 className="accordion-title">{t('story_form.advanced_options_title')}</h4>
            <span className={`accordion-icon ${showAdvancedOptions ? 'expanded' : ''}`}>
              ▼
            </span>
          </div>
          
          {showAdvancedOptions && (
            <div className="accordion-content" id="advanced-options">
            
            <div className="form-group">
              <label htmlFor="theme">{t('story_form.theme')}</label>
              <input
                type="text"
                id="theme"
                value={theme}
                onChange={(e) => setTheme(e.target.value)}
                placeholder={t('story_form.theme_placeholder')}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="tone">{t('story_form.tone')}</label>
              <DatalistInput<Tone>
                id="tone"
                value={tone}
                onChange={setTone}
                placeholder={t('story_form.tone_placeholder')}
                options={TONE_OPTIONS}
                optionTranslationKey="options.tone"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="conflictType">{t('story_form.conflict')}</label>
              <DatalistInput<ConflictType>
                id="conflictType"
                value={conflictType}
                onChange={setConflictType}
                placeholder={t('story_form.conflict_placeholder')}
                options={CONFLICT_OPTIONS}
                optionTranslationKey="options.conflict"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="endingStyle">{t('story_form.ending')}</label>
              <DatalistInput<EndingStyle>
                id="endingStyle"
                value={endingStyle}
                onChange={setEndingStyle}
                placeholder={t('story_form.ending_placeholder')}
                options={ENDING_OPTIONS}
                optionTranslationKey="options.ending"
              />
            </div>
          </div>
        )}
        </div>
        
        <button 
          type="submit" 
          className="start-story-button" 
          disabled={isLoading}
        >
          {t(isLoading ? 'story_form.starting' : 'story_form.start')}
        </button>
      </form>
    </div>
  );
};

export default StoryForm;

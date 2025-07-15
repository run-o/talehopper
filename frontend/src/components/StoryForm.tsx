import React, { useState } from 'react';
import { StoryPrompt, Character } from '../types/story';
import { useTranslation } from 'react-i18next';


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
          <input
            type="text"
            id="tone"
            list="tone-options"
            value={tone || ""}
            onChange={(e) => setTone(e.target.value as StoryPrompt["tone"] || undefined)}
            placeholder="Select or enter a tone..."
          />
          <datalist id="tone-options">
            <option value="friendly" />
            <option value="silly" />
            <option value="adventurous" />
            <option value="mysterious" />
            <option value="wholesome" />
          </datalist>
        </div>
        
        <div className="form-group">
          <label htmlFor="conflictType">{t('story_form.conflict')}</label>
          <input
            type="text"
            id="conflictType"
            list="conflict-options"
            value={conflictType || ""}
            onChange={(e) => setConflictType(e.target.value as StoryPrompt["conflict_type"] || undefined)}
            placeholder="Select or enter a conflict type..."
          />
          <datalist id="conflict-options">
            <option value="quest" />
            <option value="problem" />
            <option value="villain" />
            <option value="lost item" />
          </datalist>
        </div>
        
        <div className="form-group">
          <label htmlFor="endingStyle">{t('story_form.ending')}</label>
          <input
            type="text"
            id="endingStyle"
            list="ending-options"
            value={endingStyle || ""}
            onChange={(e) => setEndingStyle(e.target.value as StoryPrompt["ending_style"] || undefined)}
            placeholder="Select or enter an ending style..."
          />
          <datalist id="ending-options">
            <option value="happy" />
            <option value="twist" />
            <option value="moral" />
            <option value="open" />
          </datalist>
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
            <input
              type="text"
              id="characterGender"
              list="gender-options"
              value={characterGender || ""}
              onChange={(e) => setCharacterGender(e.target.value || undefined)}
              placeholder={t('story_form.character_gender')}
            />
            <datalist id="gender-options">
              <option value="Boy" />
              <option value="Girl" />
              <option value="Neutral" />
            </datalist>

            {/* Personality with Datalist */}
            <input
              type="text"
              id="characterPersonality"
              list="personality-options"
              value={characterPersonality || ""}
              onChange={(e) => setCharacterPersonality(e.target.value || undefined)}
              placeholder={t('story_form.character_personality')}
            />
            <datalist id="personality-options">
              <option value="Good" />
              <option value="Bad" />
              <option value="Neutral" />
              <option value="Kind" />
              <option value="Brave" />
              <option value="Helpful" />
              <option value="Mean" />
              <option value="Selfish" />
              <option value="Mischievous" />
              <option value="Cruel" />
              <option value="Evil" />
              <option value="Heroic" />
            </datalist>

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

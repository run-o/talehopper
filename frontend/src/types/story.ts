// Option constants for type safety and consistency
export const GENDER_OPTIONS = ['boy', 'girl', 'neutral'] as const;
export const PERSONALITY_OPTIONS = ['good', 'bad', 'neutral', 'kind', 'brave', 'helpful', 'mean', 'selfish', 'mischievous', 'cruel', 'evil', 'heroic'] as const;
export const TONE_OPTIONS = ['friendly', 'silly', 'adventurous', 'mysterious', 'wholesome'] as const;
export const CONFLICT_OPTIONS = ['quest', 'problem', 'villain', 'lost_item'] as const;
export const ENDING_OPTIONS = ['happy', 'twist', 'moral', 'open'] as const;

// Derived types from constants
export type Gender = typeof GENDER_OPTIONS[number];
export type Personality = typeof PERSONALITY_OPTIONS[number];
export type Tone = typeof TONE_OPTIONS[number];
export type ConflictType = typeof CONFLICT_OPTIONS[number];
export type EndingStyle = typeof ENDING_OPTIONS[number];

export interface Character {
  name: string;
  type: string;
  gender?: Gender;
  personality?: Personality;
}

export interface StoryPrompt {
  age: number;
  language: "english" | "french";
  length: number;
  prompt?: string;
  characters?: Character[];
  environment?: string;
  theme?: string;
  tone?: Tone;
  conflict_type?: ConflictType;
  ending_style?: EndingStyle;
}

export interface StoryRequest {
  prompt: StoryPrompt;
  history: string[];
  choice?: string;
  stage_plan?: { [key: string]: number };
}

export interface StoryResponse {
  choices: string[];
  history: string[];
  stage_plan: { [key: string]: number };
}

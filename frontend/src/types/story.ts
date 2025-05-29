export interface Character {
  name: string;
  type: string;
  gender?: string;
  personality?: string;
}

export interface StoryPrompt {
  age: number;
  language: "english" | "french";
  length: number;
  prompt?: string;
  characters?: Character[];
  environment?: string;
  theme?: string;
  tone?: "friendly" | "silly" | "adventurous" | "mysterious" | "wholesome";
  conflict_type?: "quest" | "problem" | "villain" | "lost item";
  ending_style?: "happy" | "twist" | "moral" | "open";
}

export interface StoryRequest {
  prompt: StoryPrompt;
  history: string[];
  choice?: string;
}

export interface StoryResponse {
  choices: string[];
  history: string[];
}

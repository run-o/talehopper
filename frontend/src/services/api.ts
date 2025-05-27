import { StoryRequest, StoryResponse } from '../types/story';

export const generateStory = async (request: StoryRequest): Promise<StoryResponse> => {
  try {
    const response = await fetch('/story/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error generating story:', error);
    throw error;
  }
};

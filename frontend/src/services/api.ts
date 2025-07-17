import { StoryRequest, StoryResponse } from '../types/story';

export const generateStory = async (request: StoryRequest): Promise<StoryResponse> => {
  try {
    const apiUrl = process.env.REACT_APP_API_URL || '';
    const response = await fetch(`${apiUrl}/story/generate`, {
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

export interface FeedbackRequest {
  message: string;
  email?: string;
}

export const sendFeedback = async (feedback: FeedbackRequest): Promise<void> => {
  try {
    const apiUrl = process.env.REACT_APP_API_URL || '';
    const response = await fetch(`${apiUrl}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(feedback),
    });
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
  } catch (error) {
    console.error('Error sending feedback:', error);
    throw error;
  }
};

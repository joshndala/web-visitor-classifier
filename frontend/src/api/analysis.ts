import { AnalysisResponse } from './types';

const API_BASE_URL = 'http://localhost:5000/api';  // backend URL

export const analyzeWebsite = async (url: string): Promise<AnalysisResponse> => {
    try {
      console.log('Sending request to:', `${API_BASE_URL}/generate-questions`);
      console.log('Request body:', { url });
      
      const response = await fetch(`${API_BASE_URL}/generate-questions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        console.error('Server error:', errorData);
        throw new Error(errorData.error || 'Failed to analyze website');
      }
  
      const data = await response.json();
      console.log('Response data:', data);
      return data;
    } catch (error) {
      console.error('API call error:', error);
      throw error;
    }
  };
import React, { useState } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { Typography } from '@mui/material';
import MainLayout from './components/Layout/MainLayout';
import URLInput from './components/URLInput/URLInput';
import ResultsDisplay from './components/Results/ResultsDisplay';
import theme from './styles/theme';
import { AnalysisResponse } from './api/types';

const App: React.FC = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<AnalysisResponse | undefined>();
  const [error, setError] = useState<string | undefined>();

  const handleAnalyze = async (results: AnalysisResponse) => {
    setIsAnalyzing(true);
    setError(undefined);
    try {
      setResults(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmitAnswer = async (answer: string) => {
    try {
      // Here you'll make the API call to analyze results
      console.log('Selected answer:', answer);
      // Implement the API call to /analyze-results
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit answer');
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <MainLayout>
        <div className="w-full flex flex-col items-center space-y-8">
          <URLInput 
            onAnalyze={handleAnalyze} 
            isLoading={isAnalyzing}
            onError={setError}
          />
          <ResultsDisplay 
            isLoading={isAnalyzing}
            results={results}
            onSubmitAnswer={handleSubmitAnswer}
          />
          {error && (
            <Typography color="error" sx={{ mt: 2 }}>
              {error}
            </Typography>
          )}
        </div>
      </MainLayout>
    </ThemeProvider>
  );
};

export default App;
import React, { useState } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import MainLayout from './components/Layout/MainLayout';
import URLInput from './components/URLInput/URLInput';
import ResultsDisplay from './components/Results/ResultsDisplay';
import theme from './styles/theme';

const App: React.FC = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleAnalyze = async (url: string) => {
    setIsAnalyzing(true);
    // We'll implement actual analysis later
    setTimeout(() => {
      setResults({ url, timestamp: new Date().toISOString() });
      setIsAnalyzing(false);
    }, 2000);
  };

  return (
    <ThemeProvider theme={theme}>
      <MainLayout>
        <div className="w-full flex flex-col items-center space-y-8">
          <URLInput 
            onAnalyze={handleAnalyze} 
            isLoading={isAnalyzing} 
          />
          <ResultsDisplay 
            isLoading={isAnalyzing}
            results={results}
          />
        </div>
      </MainLayout>
    </ThemeProvider>
  );
};

export default App;
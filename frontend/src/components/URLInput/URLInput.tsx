import React, { useState } from 'react';
import { TextField, Button, Card, CardContent, Typography, CircularProgress, Box } from '@mui/material';
import { analyzeWebsite } from '../../api/analysis';
import { AnalysisResponse } from '../../api/types';

interface URLInputProps {
  onAnalyze: (results: AnalysisResponse) => void;
  isLoading?: boolean;
  onError: (error: string) => void;
}

const URLInput: React.FC<URLInputProps> = ({ 
  onAnalyze, 
  isLoading = false,
  onError 
}) => {
  const [url, setUrl] = useState('');  // This was missing!

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const results = await analyzeWebsite(url);
      onAnalyze(results);
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Failed to analyze website');
    }
  };

  return (
    <Box maxWidth="md" mx="auto">
      <Card variant="outlined" className="border-primary">
        <CardContent>
          <Typography variant="h5" component="div" gutterBottom>
            How it works
          </Typography>
          <Typography variant="body1" color="textSecondary" component="ol">
            <li>Enter any website URL below</li>
            <li>We'll analyze the website's content</li>
            <li>Get insights about potential visitors</li>
          </Typography>
        </CardContent>
      </Card>

      <form onSubmit={handleSubmit} style={{ marginTop: '16px' }}>
        <TextField
          id="url"
          label="Website URL"
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com"
          fullWidth
          required
          margin="normal"
          variant="outlined"
        />
        <Typography variant="body2" color="textSecondary">
          Enter the full URL including https://
        </Typography>
        <Button
          type="submit"
          variant="contained"
          className="bg-primary text-accent"
          fullWidth
          disabled={isLoading}
          style={{ marginTop: '16px' }}
        >
          {isLoading ? (
            <CircularProgress size={24} className="text-accent" />
          ) : 'Analyze Website'}
        </Button>
      </form>
    </Box>
  );
};

export default URLInput;
import React, { useState } from 'react';
import { TextField, Button, Card, CardContent, Typography, CircularProgress, Box } from '@mui/material';

interface URLInputProps {
  onAnalyze: (url: string) => void;
  isLoading?: boolean;
}

const URLInput: React.FC<URLInputProps> = ({ 
  onAnalyze, 
  isLoading = false 
}) => {
  const [url, setUrl] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAnalyze(url);
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
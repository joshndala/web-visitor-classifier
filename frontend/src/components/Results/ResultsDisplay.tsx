import React from 'react';
import { Card, CardContent, Typography, CircularProgress, Box } from '@mui/material';

interface ResultsDisplayProps {
  isLoading?: boolean;
  results?: any;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ 
  isLoading,
  results 
}) => {
  if (isLoading) {
    return (
      <Box maxWidth="md" mx="auto" mt={4}>
        <Card variant="outlined" className="border-primary">
          <CardContent>
            <Box display="flex" justifyContent="center" alignItems="center" height="100px">
              <CircularProgress className="text-primary" />
            </Box>
          </CardContent>
        </Card>
      </Box>
    );
  }

  if (!results) {
    return null;
  }

  return (
    <Box maxWidth="md" mx="auto" mt={4}>
      <Card variant="outlined" className="border-primary">
        <CardContent>
          <Typography variant="h5" component="div" gutterBottom>
            Analysis Results
          </Typography>
          <Box className="bg-secondary p-2 rounded overflow-auto">
            <Typography variant="body2" component="pre">
              {JSON.stringify(results, null, 2)}
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ResultsDisplay;
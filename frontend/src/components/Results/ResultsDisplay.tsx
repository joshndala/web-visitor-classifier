import React, { useState } from 'react';
import { 
  Card, CardContent, Typography, CircularProgress, Box, RadioGroup, FormControlLabel, Radio, Button
} from '@mui/material';
import { AnalysisResponse } from '../../api/types';

interface ResultsDisplayProps {
  isLoading?: boolean;
  results?: AnalysisResponse;
  onSubmitAnswer?: (answer: string) => void;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ 
  isLoading,
  results,
  onSubmitAnswer
}) => {
  const [selectedOption, setSelectedOption] = useState<string>('');

  const handleSubmit = () => {
    if (selectedOption && onSubmitAnswer) {
      onSubmitAnswer(selectedOption);
    }
  };

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
          {results?.questions && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {results.questions.question}
              </Typography>
              <RadioGroup
                value={selectedOption}
                onChange={(e) => setSelectedOption(e.target.value)}
              >
                {results.questions.options.map((option, index) => (
                  <FormControlLabel
                    key={index}
                    value={option}
                    control={<Radio />}
                    label={option}
                  />
                ))}
              </RadioGroup>
              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={!selectedOption}
                className="bg-primary text-accent mt-4"
              >
                Submit Answer
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default ResultsDisplay;
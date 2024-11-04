import React from 'react';
import { Container, Box, Typography } from '@mui/material';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <Box minHeight="100vh" display="flex" flexDirection="column" className="bg-accent">
      <Container maxWidth="lg" style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <Box textAlign="center" mb={4}>
          <Typography variant="h2" component="h1" gutterBottom>
            Web Visitor Classifier
          </Typography>
          <Typography variant="h6" color="textSecondary">
            Analyze websites and understand your audience better. Simply enter a URL below, and we'll help you classify potential visitors based on the website's content.
          </Typography>
        </Box>
        
        {children}
      </Container>
    </Box>
  );
};

export default MainLayout;
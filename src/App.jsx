import React, { useState } from 'react';
import {
  Container,
  TextField,
  Button,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Grid,
  Paper,
  Alert,
  Link,
  Chip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import MedicalInformationIcon from '@mui/icons-material/MedicalInformation';
import axios from 'axios';

const App = () => {
  const [drugs, setDrugs] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const analyzeDrugs = async () => {
    if (!drugs.trim()) {
      setError('Please enter at least one drug name');
      return;
    }
    
    setLoading(true);
    setError('');
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/analyze`,
        { drugs: drugs.split(',').map(d => d.trim()) }
      );
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze drugs. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 6 }}>
      <Paper elevation={0} sx={{ 
        p: 4, 
        mb: 4, 
        backgroundColor: '#f8f9fa',
        borderBottom: '4px solid #0066cc'
      }}>
        <Grid container alignItems="center" spacing={2}>
          <Grid item>
            <MedicalInformationIcon sx={{ fontSize: 40, color: '#0066cc' }} />
          </Grid>
          <Grid item>
            <Typography variant="h3" component="h1" sx={{ 
              fontWeight: 700, 
              color: '#003366',
              fontFamily: 'Roboto Condensed'
            }}>
              PharmaIntelligence Analyzer
            </Typography>
          </Grid>
        </Grid>

        <Grid container spacing={3} sx={{ mt: 2 }} alignItems="center">
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="Enter drug names (comma-separated)"
              variant="outlined"
              value={drugs}
              onChange={(e) => setDrugs(e.target.value)}
              placeholder="Example: Adalimumab, Pembrolizumab"
              disabled={loading}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: '8px',
                  backgroundColor: 'white'
                }
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              fullWidth
              variant="contained"
              color="primary"
              size="large"
              onClick={analyzeDrugs}
              disabled={loading}
              sx={{ 
                height: '56px',
                borderRadius: '8px',
                textTransform: 'none',
                fontSize: '1rem',
                backgroundColor: '#0066cc',
                '&:hover': { backgroundColor: '#004d99' }
              }}
            >
              {loading ? <CircularProgress size={24} sx={{ color: 'white' }} /> : 'Generate Analysis'}
            </Button>
          </Grid>
        </Grid>
        
        {error && (
          <Alert severity="error" sx={{ mt: 2, borderRadius: '4px' }}>
            {error}
          </Alert>
        )}
      </Paper>

      {results.map((drugData, index) => (
        <Accordion key={index} sx={{ mb: 2, borderRadius: '8px!important' }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" sx={{ 
              fontWeight: 600,
              color: '#003366',
              fontFamily: 'Roboto Condensed'
            }}>
              {drugData.molecule}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Section title="Mechanism of Action" content={drugData.moa} />
                <Section title="Latest Development Summary" content={drugData.latest_summary} />
              </Grid>
              
              <Grid item xs={12} md={8}>
                <Typography variant="h6" gutterBottom sx={{ 
                  color: '#0066cc',
                  fontFamily: 'Roboto Condensed',
                  borderBottom: '2px solid #0066cc',
                  pb: 1
                }}>
                  News Analysis
                </Typography>
                <Grid container spacing={3}>
                  <CategorySection 
                    title="Regulatory Updates" 
                    items={drugData.regulatory_news}
                    color="#0066cc"
                  />
                  <CategorySection
                    title="Clinical Developments"
                    items={drugData.clinical_news}
                    color="#cc0000"
                  />
                  <CategorySection
                    title="Commercial Activity"
                    items={drugData.commercial_news}
                    color="#009933"
                  />
                </Grid>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      ))}
    </Container>
  );
};

const Section = ({ title, content }) => (
  <Paper elevation={0} sx={{ 
    p: 3, 
    mb: 3, 
    backgroundColor: 'white',
    borderLeft: '4px solid #0066cc',
    borderRadius: '4px'
  }}>
    <Typography variant="h6" gutterBottom sx={{ 
      fontWeight: 600,
      color: '#003366',
      fontFamily: 'Roboto Condensed'
    }}>
      {title}
    </Typography>
    <Typography variant="body1" whiteSpace="pre-wrap" sx={{ 
      lineHeight: 1.6,
      color: '#333333'
    }}>
      {content}
    </Typography>
  </Paper>
);

const CategorySection = ({ title, items, color }) => (
  <Grid item xs={12} md={4}>
    <Paper sx={{ 
      p: 2, 
      height: '100%', 
      backgroundColor: '#ffffff',
      border: `1px solid ${color}30`,
      borderRadius: '8px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
    }}>
      <Typography variant="subtitle1" gutterBottom sx={{ 
        fontWeight: 600, 
        color: color,
        fontFamily: 'Roboto Condensed',
        mb: 2
      }}>
        {title}
      </Typography>
      {items.map((item, index) => (
        <Paper key={index} elevation={0} sx={{ 
          mb: 2, 
          p: 2,
          backgroundColor: '#f8f9fa',
          borderRadius: '4px'
        }}>
          <Typography variant="body2" sx={{ 
            color: '#666666',
            mb: 1,
            whiteSpace: 'pre-wrap'
          }}>
            {item.summary}
          </Typography>
          {item.url && (
            <Link 
              href={item.url} 
              target="_blank" 
              rel="noopener"
              sx={{
                fontSize: '0.75rem',
                color: color,
                textDecoration: 'none',
                '&:hover': { textDecoration: 'underline' },
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <span>Source Article</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill={color}>
                <path d="M19 19H5V5h7V3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
              </svg>
            </Link>
          )}
        </Paper>
      ))}
    </Paper>
  </Grid>
);

export default App;

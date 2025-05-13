import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress
} from '@mui/material';
import axios from 'axios';

function App() {
  const [preferences, setPreferences] = useState({
    preferred_type: '',
    budget_level: '',
    activities: []
  });
  const [location, setLocation] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePreferenceChange = (event) => {
    setPreferences({
      ...preferences,
      [event.target.name]: event.target.value
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      // First get location coordinates
      const locationResponse = await axios.get(`http://localhost:5000/api/location?address=${encodeURIComponent(location)}`);
      const locationData = locationResponse.data;

      if (!locationData) {
        throw new Error('Could not find location');
      }

      // Then get recommendations
      const response = await axios.post('http://localhost:5000/api/recommendations', {
        preferences,
        location: locationData
      });

      setRecommendations(response.data.recommendations);
    } catch (err) {
      setError(err.message || 'An error occurred while fetching recommendations');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          AI Travel Recommender
        </Typography>

        <Box component="form" onSubmit={handleSubmit} sx={{ mb: 4 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Preferred Type</InputLabel>
                <Select
                  name="preferred_type"
                  value={preferences.preferred_type}
                  onChange={handlePreferenceChange}
                  label="Preferred Type"
                >
                  <MenuItem value="beach">Beach</MenuItem>
                  <MenuItem value="city">City</MenuItem>
                  <MenuItem value="cultural">Cultural</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Budget Level</InputLabel>
                <Select
                  name="budget_level"
                  value={preferences.budget_level}
                  onChange={handlePreferenceChange}
                  label="Budget Level"
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Location"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Enter city or address"
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Get Recommendations'}
              </Button>
            </Grid>
          </Grid>
        </Box>

        {error && (
          <Typography color="error" align="center" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}

        <Grid container spacing={2}>
          {recommendations.map((rec, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {rec.destination.name}
                  </Typography>
                  <Typography color="textSecondary" gutterBottom>
                    Type: {rec.destination.type}
                  </Typography>
                  <Typography color="textSecondary" gutterBottom>
                    Climate: {rec.destination.climate}
                  </Typography>
                  <Typography color="textSecondary" gutterBottom>
                    Best Season: {rec.destination.best_season}
                  </Typography>
                  <Typography color="textSecondary" gutterBottom>
                    Budget Level: {rec.destination.budget_level}
                  </Typography>
                  <Typography variant="body2">
                    Activities: {rec.destination.activities.join(', ')}
                  </Typography>
                  <Typography variant="h6" color="primary" sx={{ mt: 2 }}>
                    Match Score: {(rec.score * 100).toFixed(1)}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
}

export default App; 
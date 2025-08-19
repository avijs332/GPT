import { useState } from 'react';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Autocomplete,
  Paper,
} from '@mui/material';

const poiOptions = ['Hospitals', 'Schools', 'Shopping Centers', 'Train Stations', 'Parks'];

export const PlanPage = () => {
  const [numRoutes, setNumRoutes] = useState(1);
  const [selectedPOIs, setSelectedPOIs] = useState<string[]>([]);

  const handleSubmit = () => {
    // TODO: Replace with API call or navigation
    console.log('Submitting:', { numRoutes, selectedPOIs });
  };

  return (
    <Container maxWidth="md" sx={{ mt: 6 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom>
          Plan New Bus Routes
        </Typography>

        <Box sx={{ mt: 3 }}>
          <TextField
            label="Number of Bus Routes"
            type="number"
            fullWidth
            value={numRoutes}
            onChange={(e) => setNumRoutes(Number(e.target.value))}
            inputProps={{ min: 1 }}
            sx={{ mb: 3 }}
          />

          <Autocomplete
            multiple
            options={poiOptions}
            value={selectedPOIs}
            onChange={(_event, newValue) => setSelectedPOIs(newValue)}
            renderInput={(params) => <TextField {...params} label="Select Interest Points" />}
          />

          <Button
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mt: 4 }}
            onClick={handleSubmit}
          >
            Generate Route Plan
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}

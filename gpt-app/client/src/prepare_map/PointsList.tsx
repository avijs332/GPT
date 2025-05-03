import { useState } from 'react';
import {
  List,
  ListItem,
  Select,
  MenuItem,
  TextField,
  FormControl,
  InputLabel,
  Box,
  Typography
} from '@mui/material';
import { useCity } from '../providers/city-provider';
import { OsmLocation } from '../hooks';

const handleChange = <T extends OsmLocation>(id: string, stateDelete: T[], setStateInsert: React.Dispatch<React.SetStateAction<T[]>>, setStateDelete: React.Dispatch<React.SetStateAction<T[]>>, mutate?: (x:T) => void) => {
  const point = stateDelete.find(x => x.osm_id === `${id}`)
  
  if (point) {
    mutate?.(point);
    setStateDelete(prev => [...prev.filter(x => x.osm_id !== point.osm_id)]);
    setStateInsert(prev => [...prev, point]);
  }
}

export const PointsList = () => {
  const { interestPoints, centralPoints, setInterestPoints, setCentralPoints} = useCity();

  const handleTypeChange = (id: string, newType: string) => {
    if (newType === 'interest point') {
      handleChange(id, centralPoints, setInterestPoints, setCentralPoints, x => x.grade = 1);

      return;
    }

    if (newType === 'central station') {
      handleChange(id, interestPoints, setCentralPoints, setInterestPoints, x => delete x.grade);

      return;
    }
    // setItems(prev =>
    //   prev.map(item =>
    //     item.id === id
    //       ? { ...item, type: newType, grade: newType === 'interest point' ? (item.grade ?? 1) : null }
    //       : item
    //   )
    // );
  };

  const getMenuValue = (id: string) => (
    interestPoints.find(x => x.osm_id === id) ?
      'interest point' :
      'central station'
  );

  const handleGradeChange = (id: string, grade: number) => {
    setInterestPoints(prev =>
      prev.map(item =>
        item.osm_id === id ? { ...item, grade } : item
      )
    );
  };

  return (
    <List>
      {interestPoints.map(point => (
        <ListItem key={point.osm_id} alignItems="flex-start">
          <Box display="flex" flexDirection="column" width="100%">
            <Typography variant="subtitle1">{point.display_name}</Typography>

            <FormControl fullWidth margin="dense">
              <InputLabel>Type</InputLabel>
              <Select
                disabled
                value={'interest point'}
                label="Type"
                onChange={(e) => handleTypeChange(point.osm_id, e.target.value)}
              >
                <MenuItem value="interest point">Interest Point</MenuItem>
              </Select>
            </FormControl>

            {getMenuValue(point.osm_id) === 'interest point' && (
              <TextField
                label="Grade (1-10)"
                type="number"
                margin="dense"
                inputProps={{ min: 1, max: 10 }}
                value={point.grade ?? ''}
                onChange={(e) => handleGradeChange(point.osm_id, parseInt(e.target.value) || 1)}
                fullWidth
              />
            )}
          </Box>
        </ListItem>
      ))}
      {centralPoints.map(point => (
        <ListItem key={point.osm_id} alignItems="flex-start">
          <Box display="flex" flexDirection="column" width="100%">
            <Typography variant="subtitle1">{point.display_name}</Typography>

            <FormControl fullWidth margin="dense">
              <InputLabel>Type</InputLabel>
              <Select
                disabled
                value={'central station'}
                label="Type"
                onChange={(e) => handleTypeChange(point.osm_id, e.target.value)}
              >
                <MenuItem value="central station">Central Station</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </ListItem>
      ))}
    </List>
  );
};
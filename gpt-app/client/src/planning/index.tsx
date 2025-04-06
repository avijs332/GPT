import { Button, TextField, FormLabel, Stack, Box, Typography } from "@mui/material";
import { useForm } from "react-hook-form"
import { useNavigate } from "react-router";

import { CitySelect } from "./CitySelect";
import { useCity } from "../providers/city-provider";

export const PlanningPage = () => {
  const { register, watch } = useForm();
  const navigate = useNavigate();
  const { setBusCount } = useCity();

  const cityName = watch('cityName') as string;

  const handleSubmit = () => { 
    navigate('/prepare')
    setBusCount(+watch('busCount'));
  };

  return (
    <Box width='50%' justifySelf='center' bgcolor='rgb(70, 75, 178)' padding='20px' borderRadius='10px'>
      <form>
        <Stack spacing={2}>
        <Typography alignSelf='center' fontSize='30px'>GPT - Generative Public Transport</Typography>
          <Stack spacing={0.5}>
            <FormLabel>City Name</FormLabel>
            <TextField {...register('cityName')} />
          </Stack>
          <CitySelect cityName={cityName} />
          <Stack spacing={0.5}>
            <FormLabel>Number of Bus Lanes</FormLabel>
            <TextField {...register('busCount')} type="number" />            
          </Stack>
          <Button onClick={handleSubmit}>Submit</Button>
        </Stack>
      </form>
    </Box>
  );
};
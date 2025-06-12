import { TextField, FormLabel, Stack, Typography } from "@mui/material";
import { useForm } from "react-hook-form"
import { useNavigate } from "react-router";

import { CitySelect } from "./CitySelect";
import { useCity } from "../providers/city-provider";
import { Button, MotionWrapper } from "../common";

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
    <MotionWrapper shouldPad={true} shouldSpread={false}>
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
          <Button onClick={handleSubmit} label='Submit' />
        </Stack>
      </form>
    </MotionWrapper>
  );
};
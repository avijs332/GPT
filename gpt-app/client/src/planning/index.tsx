import { Button, TextField, FormLabel, Stack, Box, Typography } from "@mui/material";
import { useForm } from "react-hook-form"
import { useNavigate } from "react-router";

export const PlanningPage = () => {
  const { register } = useForm();
  const navigate = useNavigate();

  const handleSubmit = () => { console.log('nav'); navigate('/map') };

  return (
    <Box width='50%' justifySelf='center' bgcolor='rgb(70, 75, 178)' padding='20px' borderRadius='10px'>
      <form onSubmit={handleSubmit}>
        <Stack spacing={2}>
        <Typography alignSelf='center' fontSize='30px'>GPT - Generative Public Transport</Typography>
          <Stack spacing={0.5}>
            <FormLabel>City Name</FormLabel>
            <TextField {...register('cityName')} />
          </Stack>
          <Stack spacing={0.5}>
            <FormLabel>Number of Bus Lanes</FormLabel>
            <TextField {...register('busCount')} type="number" />            
          </Stack>
          <Button type="submit">Submit</Button>
        </Stack>
      </form>
    </Box>
  );
};
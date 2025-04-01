import { Button, TextField } from "@mui/material";
import { useForm } from "react-hook-form"
import { useNavigate } from "react-router";

export const PlanningPage = () => {
  const {  } = useForm();
  const navigate = useNavigate();

  const handleSubmit = () => { console.log('nav'); navigate('/map') };

  return (
    <form onSubmit={handleSubmit}>
      <TextField name='cityName'>
      </TextField>      
      <TextField name='busCount'>
      </TextField>
      <Button type="submit">Submit</Button>
    </form>
  );
};
import { FC } from "react"
import { useNavigate } from "react-router-dom";
import { Stack, Button, Typography } from "@mui/material";

interface BackButtonProps {
  route?: string
};

export const BackButton: FC<BackButtonProps> = ({ route }) => {
  const navigate = useNavigate();

  const onClick = () => { route ? navigate(route) : navigate(-1) };

  return (
    <Stack alignItems='center' bgcolor='rgb(70, 75, 178)' padding='20px'>
      <Button onClick={onClick}>
        <Typography>
          Go Back
        </Typography>
      </Button>
    </Stack>
  );
};

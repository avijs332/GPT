import { FC } from "react"
import { useNavigate } from "react-router-dom";
import { Stack, Button, Typography } from "@mui/material";

import { useCity } from "../providers/city-provider";

interface BackButtonProps {
  route?: string;
  label?: string;
  fullWidth?: boolean;
};

export const BackButton: FC<BackButtonProps> = ({ route, label, fullWidth }) => {
  const navigate = useNavigate();
  const { reset } = useCity();

  const onClick = () => { 
    if (route) {
      navigate(route);
    } else {
      navigate(-1)
    }

    // reset();
  };

  return (
    <Stack alignItems='center' bgcolor='rgb(70, 75, 178)' padding='20px' width={ fullWidth ? '100%' : 'initial'}>
      <Button onClick={onClick} fullWidth={!!fullWidth}>
        <Typography>
          { label || 'Go Back'}
        </Typography>
      </Button>
    </Stack>
  );
};

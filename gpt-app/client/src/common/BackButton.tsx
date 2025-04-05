import { FC } from "react"
import { useNavigate } from "react-router-dom";
import { Stack, Button, Typography } from "@mui/material";

interface BackButtonProps {
  route?: string;
  label?: string;
  fullWidth?: boolean;
};

export const BackButton: FC<BackButtonProps> = ({ route, label, fullWidth }) => {
  const navigate = useNavigate();

  const onClick = () => { route ? navigate(route) : navigate(-1) };

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

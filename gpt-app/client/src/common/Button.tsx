import { FC } from "react";
import { Stack, Button as MuiButton, Typography } from "@mui/material";

export interface ButtonProps {
  label: string;
  onClick?: React.MouseEventHandler<HTMLButtonElement>;
  fullWidth?: true;
};

export const Button: FC<ButtonProps> = ({ fullWidth, label, onClick }) => (
  <Stack alignItems='center' bgcolor='rgb(70, 75, 178)' padding='20px' width={ fullWidth ? '100%' : 'initial'}>
    <MuiButton onClick={onClick} fullWidth={!!fullWidth}>
      <Typography>
        { label }
      </Typography>
    </MuiButton>
  </Stack>
);

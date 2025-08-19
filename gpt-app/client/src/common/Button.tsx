import { PropsWithChildren } from "react";
import { Stack, Button as MuiButton, Typography } from "@mui/material";

export interface ButtonProps {
  label?: string;
  onClick?: React.MouseEventHandler<HTMLButtonElement>;
  fullWidth?: true;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
};

export const Button = ({ fullWidth, label, onClick, disabled, type, children }: PropsWithChildren<ButtonProps>) => (
  <Stack alignItems='center' padding='20px' width={ fullWidth ? '100%' : 'initial'}>
    <MuiButton variant="contained" onClick={onClick} fullWidth={!!fullWidth} disabled={disabled} type={type}>
      <Typography>
        {
          children ||
          label
        }
      </Typography>
    </MuiButton>
  </Stack>
);

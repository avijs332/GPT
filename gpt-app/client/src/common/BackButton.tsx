import { FC } from "react"
import { useNavigate } from "react-router-dom";

import { Button, ButtonProps } from "./Button";
import { useCity } from "../providers/city-provider";
import { useLayout } from "../layout/LayoutWrapper";

interface BackButtonProps extends Omit<ButtonProps, 'label'> {
  route?: string;
  label?: string
};

export const BackButton: FC<BackButtonProps> = ({ onClick, route, label, ...props }) => {
  const navigate = useNavigate();
  const { reset } = useCity();
  const { unSpread } = useLayout();

  const goBackOnClick = () => { 
    if (route) {
      navigate(route);
    } else {
      navigate('/')
      reset()
    };
    
    unSpread();
  };

  return (
    <Button {...props} label={label || 'Go Back'} onClick={onClick || goBackOnClick}  />
  );
};

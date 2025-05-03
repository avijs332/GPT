import { FC } from "react"
import { useNavigate } from "react-router-dom";

import { Button, ButtonProps } from "./Button";
import { useCity } from "../providers/city-provider";

interface BackButtonProps extends Omit<ButtonProps, 'label'> {
  route?: string;
  label?: string
};

export const BackButton: FC<BackButtonProps> = ({ onClick, route, label, ...props }) => {
  const navigate = useNavigate();
  const { reset } = useCity();

  const goBackOnClick = () => { 
    if (route) {
      navigate(route);
    } else {
      navigate('/')
      reset()
    };
  };

  return (
    <Button {...props} label={label || 'Go Back'} onClick={onClick || goBackOnClick}  />
  );
};

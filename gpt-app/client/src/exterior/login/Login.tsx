import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { TextField, Stack, Typography, InputAdornment, IconButton } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';

import { useAuth } from '../../providers/auth-provider';
import { Button, MotionWrapper } from '../../common';

export const Login = () => {
  const { login, loginState } = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  const { register, getValues, formState } = useForm();
  console.log('Login form state:', formState);
  console.log('Login form state:', Object.keys(formState.errors).length);

  const handleLogin = (event: React.FormEvent) => {
    event.preventDefault();

    try {
      login(getValues('username'), getValues('password'));
    } catch (err) {
      console.error('Login error:', err);
    }
  };

  return (
    <MotionWrapper shouldPad={true} shouldSpread={false}>
      <form onSubmit={handleLogin} autoComplete="on">
        <Stack spacing={3} alignItems="center" >
          <img src="/gpt-icon-white.png" alt="GPT Logo" style={{ width: 150, marginBottom: 8 }} />
          <Typography variant="h4" fontWeight={600}>Sign In</Typography>
          <TextField
            label="Username"
            {...register('username', { required: true })}
            required
            error={!!formState.errors.username}
            fullWidth
            autoFocus
            autoComplete="username"
          />
          <TextField
            label="Password"
            type={showPassword ? 'text' : 'password'}
            fullWidth
            autoComplete="current-password"
            required
            error={!!formState.errors.password}
            helperText={formState.errors.password ? 'Password is required' : ''}
            {...register('password', { required: true })}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={() => setShowPassword((show) => !show)}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              )
            }}
          />
          {loginState.isPending ? (
            <Button fullWidth disabled>
              <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span className="MuiCircularProgress-root MuiCircularProgress-indeterminate" style={{ width: 24, height: 24, marginRight: 8 }}>
                  <svg viewBox="22 22 44 44" style={{ width: 24, height: 24 }}>
                    <circle
                      className="MuiCircularProgress-circle"
                      cx="44"
                      cy="44"
                      r="20.2"
                      fill="none"
                      strokeWidth="3.6"
                      stroke="#646cff"
                      strokeDasharray="80,200"
                      strokeDashoffset="0"
                      strokeLinecap="round"
                    />
                  </svg>
                </span>
                Signing in...
              </span>
            </Button>
          ) : (
            <Button label="Sign In" fullWidth type='submit'/>
          )}
            <Typography variant="body2" color="text.secondary">
              Don&apos;t have an account?{' '}
              <span style={{ color: '#646cff', cursor: 'pointer' }}>
                <Link
                  to="/register"
                  style={{ color: '#646cff', textDecoration: 'none' }}
                >
                  Register
                </Link>
              </span>
            </Typography>
        </Stack>
      </form>
    </MotionWrapper>
  );
};
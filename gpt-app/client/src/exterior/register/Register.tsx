import { useState } from 'react';
import { TextField, Stack, Typography, InputAdornment, IconButton, Alert } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../providers/auth-provider';
import { Button, MotionWrapper } from '../../common';

export const Register = () => {
  const { register, registerState } = useAuth();
  const { register: registerField, handleSubmit, formState: { errors } } = useForm();
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (data: any) => {
    setError(null);
    try {
      register({
        name: data.name,
        username: data.username,
        email: data.email,
        password: data.password
      });
    } catch (err) {
      setError('Registration failed. Please try again.');
    }
  };

  return (
    <MotionWrapper shouldPad={true} shouldSpread={false}>
      <form onSubmit={handleSubmit(onSubmit)} autoComplete="on">
        <Stack spacing={3} alignItems="center">
          <img src="/gpt-icon-white.png" alt="GPT Logo" style={{ width: 150, marginBottom: 8 }} />
          <Typography variant="h4" fontWeight={600}>Register</Typography>
          <TextField
            label="Name"
            fullWidth
            autoFocus
            autoComplete="name"
            required
            {...registerField('name', { required: 'Name is required' })}
            error={!!errors.name}
          />
          <TextField
            label="Username"
            fullWidth
            autoComplete="username"
            required
            {...registerField('username', { required: 'Username is required' })}
            error={!!errors.username}
          />
          <TextField
            label="Email"
            type="email"
            fullWidth
            autoComplete="email"
            required
            {...registerField('email', { required: 'Email is required' })}
            error={!!errors.email}
          />
          <TextField
            label="Password"
            type={showPassword ? 'text' : 'password'}
            fullWidth
            autoComplete="new-password"
            required
            {...registerField('password', { required: 'Password is required' })}
            error={!!errors.password}
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
          {error && <Alert severity="error">{error}</Alert>}
          {registerState.isSuccess && <Alert severity="success">Registration successful! Redirecting...</Alert>}
          <Button label={registerState.isPending ? 'Registering...' : 'Register'} fullWidth type="submit" />
          <Typography variant="body2" color="text.secondary">
            Already have an account?{' '}
            <Link to="/login" style={{ color: '#646cff', textDecoration: 'underline' }}>Sign In</Link>
          </Typography>
        </Stack>
      </form>
    </MotionWrapper>
  );
};
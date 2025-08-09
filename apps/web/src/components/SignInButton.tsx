import React from 'react';
import { useClerk } from '@clerk/nextjs';

const SignInButton: React.FC = () => {
  const { openSignIn } = useClerk();
  return (
    <button onClick={() => openSignIn({})}>Sign In</button>
  );
};

export default SignInButton;

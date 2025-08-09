import React from 'react';
import { useClerk } from '@clerk/nextjs';

const SignOutButton: React.FC = () => {
  const { signOut } = useClerk();
  return (
    <button onClick={() => signOut({ redirectUrl: '/' })}>Sign Out</button>
  );
};

export default SignOutButton;

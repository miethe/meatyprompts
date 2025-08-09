import React from 'react';
import SignInButton from '@/components/SignInButton';

export default function Unauthorized() {
  return (
    <main style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#18181b' }}>
      <h1 style={{ color: '#fff', fontSize: '2rem', marginBottom: '2rem' }}>401 - Unauthorized</h1>
      <p style={{ color: '#fff' }}>You must be signed in to access this page.</p>
      <div style={{ marginTop: '2rem' }}>
        <SignInButton />
      </div>
    </main>
  );
}

import React from 'react';

// Always use the backend API URL for auth
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const GITHUB_LOGIN_URL = `${API_URL}/auth/github/login`;

export default function Login() {
  return (
    <main style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#18181b' }}>
      <h1 style={{ color: '#fff', fontSize: '2rem', marginBottom: '2rem' }}>Sign in to MeatyPrompts</h1>
      <a
        href={GITHUB_LOGIN_URL}
        style={{
          background: '#24292f',
          color: '#fff',
          padding: '1rem 2rem',
          borderRadius: '0.5rem',
          textDecoration: 'none',
          fontWeight: 'bold',
          fontSize: '1.2rem',
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
        }}
      >
        <span style={{ marginRight: '0.5rem' }}>🐙</span> Sign in with GitHub
      </a>
    </main>
  );
}

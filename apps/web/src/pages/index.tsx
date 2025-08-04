import React from 'react';

export default function Home() {
  return (
    <main style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      <h1>Welcome to {{ project_name }} (Web)</h1>
    </main>
  );
}
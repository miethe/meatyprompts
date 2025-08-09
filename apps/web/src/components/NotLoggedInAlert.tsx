import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

function getCookie(name: string): string | undefined {
  if (typeof document === 'undefined') return undefined;
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : undefined;
}

const NotLoggedInAlert: React.FC = () => {
  const [show, setShow] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Only show on client
    if (typeof window === 'undefined') return;
    // Don't show on /login
    if (router.pathname === '/login') return;
    // Check for session cookie
    const session = getCookie('session') || getCookie('meatyprompts_session');
    if (!session) {
      setShow(true);
    } else {
      setShow(false);
    }
  }, [router.pathname]);

  if (!show) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: 24,
      left: 0,
      right: 0,
      margin: '0 auto',
      maxWidth: 400,
      background: '#18181b',
      color: '#fff',
      padding: '1rem 2rem',
      borderRadius: '0.5rem',
      boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
      textAlign: 'center',
      zIndex: 9999,
    }}>
      <span>⚠️ You aren&apos;t logged in.</span>
    </div>
  );
};

export default NotLoggedInAlert;

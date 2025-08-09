import React from 'react';

interface ToastProps {
  message: string;
}

const Toast: React.FC<ToastProps> = ({ message }) => (
  <>
    <div
      role="status"
      className="toast"
    >
      {message}
    </div>
    <style jsx>{`
      .toast {
        position: fixed;
        bottom: var(--toast-spacing-bottom, 1rem);
        right: var(--toast-spacing-right, 1rem);
        background: var(--toast-bg, #1a202c);
        color: var(--toast-color, #fff);
        padding: var(--toast-padding, 1rem 1.5rem);
        border-radius: var(--toast-radius, 0.5rem);
        box-shadow: var(--toast-shadow, 0 2px 8px rgba(0,0,0,0.15));
        z-index: var(--toast-z-index, 1000);
      }
    `}</style>
  </>
);

export default Toast;

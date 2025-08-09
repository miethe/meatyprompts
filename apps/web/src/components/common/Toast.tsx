import React from 'react';

interface ToastProps {
  message: string;
}

const Toast: React.FC<ToastProps> = ({ message }) => (
  <div
    role="status"
    className="fixed bottom-4 right-4 bg-gray-900 text-white px-4 py-2 rounded shadow"
  >
    {message}
  </div>
);

export default Toast;

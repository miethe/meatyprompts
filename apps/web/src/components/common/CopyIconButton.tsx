import React, { useState } from 'react';
import { Copy } from 'lucide-react';

interface CopyIconButtonProps {
  text: string;
}

const CopyIconButton: React.FC<CopyIconButtonProps> = ({ text }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text to clipboard', err);
    }
  };

  return (
    <button aria-label="Copy to clipboard" onClick={handleCopy} className="ml-2 text-gray-400 hover:text-gray-200">
      <Copy className="w-4 h-4" />
      <span
        className="sr-only"
        aria-live="polite"
        aria-atomic="true"
      >
        {copied ? 'Text copied to clipboard' : ''}
      </span>
    </button>
  );
};

export default CopyIconButton;

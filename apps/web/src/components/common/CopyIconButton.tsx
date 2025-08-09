import React, { useState } from 'react';
import { Copy } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import Toast from './Toast';

interface CopyIconButtonProps {
  text: string;
}

const CopyIconButton: React.FC<CopyIconButtonProps> = ({ text }) => {
  const [copied, setCopied] = useState(false);
  const { t } = useTranslation();

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error(t('copy.error'), err);
    }
  };

  return (
    <>
      <button
        aria-label={t('copy.buttonLabel')}
        onClick={handleCopy}
        className="ml-2 text-gray-400 hover:text-gray-200"
      >
        <Copy className="w-4 h-4" />
        <span className="sr-only" aria-live="polite" aria-atomic="true">
          {copied ? t('copy.success') : ''}
        </span>
      </button>
      {copied && <Toast message={t('copy.success')} />}
    </>
  );
};

export default CopyIconButton;

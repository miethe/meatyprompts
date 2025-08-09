import React, { useState } from 'react';
import { Copy, ChevronDown } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import type { Prompt } from '../../types/Prompt';
import Toast from './Toast';
import { copyText } from '../../lib/clipboard';
import { toBody, toFrontMatter, toJson } from '../../lib/formatters/promptCopy';
import { track } from '../../lib/analytics';

interface CopyMenuProps {
  prompt: Prompt;
  source: 'card' | 'detail';
}

const CopyMenu: React.FC<CopyMenuProps> = ({ prompt, source }) => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [toast, setToast] = useState('');

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(''), 2000);
  };

  const handleCopy = async (variant: 'body' | 'front_matter' | 'json') => {
    let text = '';
    if (variant === 'front_matter') text = toFrontMatter(prompt);
    else if (variant === 'json') text = toJson(prompt);
    else text = toBody(prompt);
    await copyText(text);
    track('prompt_copied', {
      prompt_id: prompt.id,
      variant,
      source,
      timestamp: Date.now(),
    });
    const variantLabel =
      variant === 'front_matter' ? t('copy.frontMatter') : variant === 'json' ? t('copy.json') : t('copy.body');
    showToast(t('toast.copied', { variant: variantLabel }));
    setOpen(false);
  };

  return (
    <div
      className="relative inline-block text-left"
      role="group"
      aria-label={t('copy.menuGroup')}
      onClick={(e) => e.stopPropagation()}
    >
      <button
        aria-label={t('copy.quick')}
        onClick={() => handleCopy('body')}
        className="ml-2 text-gray-400 hover:text-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
      >
        <Copy className="w-4 h-4" />
      </button>
      <button
        aria-label={t('copy.menuTitle')}
        onClick={() => setOpen(!open)}
        className="ml-1 text-gray-400 hover:text-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
      >
        <ChevronDown className="w-4 h-4" />
      </button>
      {open && (
        <div
          role="menu"
          className="absolute right-0 mt-2 w-52 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-10 dark:text-gray-400 text-gray-700"
        >
          <button
            role="menuitem"
            className="block px-4 py-2 text-sm text-left w-full hover:bg-gray-100"
            onClick={() => handleCopy('body')}
          >
            {t('copy.body')}
          </button>
          <button
            role="menuitem"
            className="block px-4 py-2 text-sm text-left w-full hover:bg-gray-100"
            onClick={() => handleCopy('front_matter')}
          >
            {t('copy.frontMatter')}
          </button>
          <button
            role="menuitem"
            className="block px-4 py-2 text-sm text-left w-full hover:bg-gray-100"
            onClick={() => handleCopy('json')}
          >
            {t('copy.json')}
          </button>
        </div>
      )}
      {toast && <Toast message={toast} />}
    </div>
  );
};

export default CopyMenu;

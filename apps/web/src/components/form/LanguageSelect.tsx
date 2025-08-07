import React from 'react';
import { LANGUAGE_OPTIONS, Language } from '../CodeEditor';

interface LanguageSelectProps {
  value: Language;
  onChange: (lang: Language) => void;
  disabled?: boolean;
  className?: string;
}

const LanguageSelect: React.FC<LanguageSelectProps> = ({ value, onChange, disabled = false, className = '' }) => (
  <select
    className={`mt-1 mb-2 text-black border-gray-300 rounded-md ${className}`}
    value={value}
    onChange={e => onChange(e.target.value as Language)}
    disabled={disabled}
  >
    {LANGUAGE_OPTIONS.map(opt => (
      <option key={opt} value={opt}>{opt}</option>
    ))}
  </select>
);

export default LanguageSelect;

import React, { useState } from 'react';
import { LucideIcon } from 'lucide-react';
import { useTheme } from '@/theme';

type ThemedButtonProps = {
  label: string;
  Icon: LucideIcon;
  onClick?: () => void;
};

const ThemedButton: React.FC<ThemedButtonProps> = ({ label, Icon, onClick }) => {
  const { theme } = useTheme();
  const [hovered, setHovered] = useState(false);
  const background = hovered ? theme.colors.primaryHover : theme.colors.primary;

  return (
    <button
      type="button"
      className="flex flex-col items-center justify-center p-4 shadow-md transition-colors"
      style={{
        backgroundColor: background,
        color: theme.colors.text,
        borderRadius: theme.borderRadius,
      }}
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <Icon size={24} />
      <span className="mt-1 text-sm font-medium">{label}</span>
    </button>
  );
};

export default ThemedButton;

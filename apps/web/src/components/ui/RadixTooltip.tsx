import * as Tooltip from '@radix-ui/react-tooltip';
import React from 'react';

interface RadixTooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
}

const RadixTooltip: React.FC<RadixTooltipProps> = ({ content, children }) => (
  <Tooltip.Provider delayDuration={200}>
    <Tooltip.Root>
      <Tooltip.Trigger asChild>{children}</Tooltip.Trigger>
      <Tooltip.Portal>
        <Tooltip.Content
          side="top"
          align="center"
          className="z-50 px-2 py-1 text-xs text-white bg-black rounded shadow-lg max-w-xs"
          sideOffset={6}
        >
          {content}
          <Tooltip.Arrow className="fill-black" />
        </Tooltip.Content>
      </Tooltip.Portal>
    </Tooltip.Root>
  </Tooltip.Provider>
);

export default RadixTooltip;

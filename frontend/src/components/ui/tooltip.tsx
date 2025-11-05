import { ReactNode } from 'react';

interface TooltipProviderProps {
  children: ReactNode;
}

interface TooltipProps {
  children: ReactNode;
  open?: boolean;
}

interface TooltipTriggerProps {
  children: ReactNode;
  asChild?: boolean;
}

interface TooltipContentProps {
  children: ReactNode;
}

export function TooltipProvider({ children }: TooltipProviderProps) {
  return <>{children}</>;
}

export function Tooltip({ children, open }: TooltipProps) {
  return <div className="relative inline-block">{children}</div>;
}

export function TooltipTrigger({ children, asChild }: TooltipTriggerProps) {
  return <div>{children}</div>;
}

export function TooltipContent({ children }: TooltipContentProps) {
  return (
    <div className="absolute z-10 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-sm tooltip">
      {children}
    </div>
  );
}

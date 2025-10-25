// UI Refactor: Replaced custom Card with shadcn/ui Card component
// This maintains the same API while using shadcn/ui styling
import { Card as ShadcnCard } from './ui/card';
import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
}

export function Card({ children, className = '' }: CardProps) {
  return (
    <ShadcnCard className={className}>
      {children}
    </ShadcnCard>
  );
}


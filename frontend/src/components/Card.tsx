<<<<<<< HEAD
// UI Refactor: Replaced custom Card with shadcn/ui Card component
// This maintains the same API while using shadcn/ui styling with Campsite design
import { Card as ShadcnCard } from './ui/card';
import type { ReactNode } from 'react';
import { cn } from '../lib/utils';
=======
import type { ReactNode } from 'react';
>>>>>>> main-holder

interface CardProps {
  children: ReactNode;
  className?: string;
}

export function Card({ children, className = '' }: CardProps) {
  return (
<<<<<<< HEAD
    <ShadcnCard className={cn("rounded-xl border border-border", className)}>
      {children}
    </ShadcnCard>
=======
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
      {children}
    </div>
>>>>>>> main-holder
  );
}


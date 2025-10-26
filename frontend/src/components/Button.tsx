// UI Refactor: Replaced custom Button with shadcn/ui Button component
// This maintains the same API while using shadcn/ui styling and variants
import { Button as ShadcnButton } from './ui/button';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'tertiary';
  size?: 'sm' | 'md' | 'lg';
  children: ReactNode;
}

export function Button({ 
  variant = 'primary', 
  size = 'md',
  children, 
  className = '',
  ...props 
}: ButtonProps) {
  // Map custom variants to shadcn/ui variants
  const shadcnVariant = variant === 'primary' ? 'default' : 
                       variant === 'secondary' ? 'secondary' : 
                       'outline';
  
  const shadcnSize = size === 'sm' ? 'sm' : 
                    size === 'lg' ? 'lg' : 
                    'default';

  return (
    <ShadcnButton 
      variant={shadcnVariant}
      size={shadcnSize}
      className={className}
      {...props}
    >
      {children}
    </ShadcnButton>
  );
}


<<<<<<< HEAD
// UI Refactor: Replaced custom Button with shadcn/ui Button component
// This maintains the same API while using shadcn/ui styling and variants
import { Button as ShadcnButton } from './ui/button';
=======
>>>>>>> main-holder
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
<<<<<<< HEAD
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
=======
  // Base styles for all buttons
  const baseStyles = 'rounded-lg font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2';
  
  // Size variants
  const sizeStyles = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-4 py-2',
    lg: 'text-base px-6 py-3',
  };
  
  // Color variants - all white backgrounds
  const variantStyles = {
    primary: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 active:bg-gray-100 shadow-sm hover:shadow-md',
    secondary: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 active:bg-gray-100 shadow-sm hover:shadow-md',
    tertiary: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 active:bg-gray-100 shadow-sm hover:shadow-md',
  };

  return (
    <button 
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
>>>>>>> main-holder
  );
}


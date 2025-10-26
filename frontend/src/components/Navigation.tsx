<<<<<<< HEAD
// UI Refactor: Updated to use shadcn/ui design tokens with dark mode toggle
// Maintains the same layout while using the design system colors
import { Sparkles } from 'lucide-react';
import { ModeToggle } from './ModeToggle';

export function Navigation() {
  return (
    <nav className="glass border-b border-border">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <div className="flex justify-between items-center h-20">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-xl">
              <Sparkles className="w-6 h-6 text-primary-foreground" />
            </div>
            <span className="text-xl font-semibold text-foreground tracking-tight">LeadForge</span>
          </div>
          <ModeToggle />
=======
import { Sparkles } from 'lucide-react';

export function Navigation() {
  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-center items-center h-16">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center w-8 h-8 bg-gray-700 rounded-lg">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-semibold text-gray-900">LeadForge</span>
          </div>
>>>>>>> main-holder
        </div>
      </div>
    </nav>
  );
}


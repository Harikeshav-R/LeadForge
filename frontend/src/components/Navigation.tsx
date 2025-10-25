// UI Refactor: Updated to use shadcn/ui design tokens for consistent styling
// Maintains the same layout while using the design system colors
import { Sparkles } from 'lucide-react';

export function Navigation() {
  return (
    <nav className="bg-background border-b border-border">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        {/* Added more generous horizontal padding */}
        <div className="flex justify-center items-center h-20">
          {/* Increased height for better visual balance */}
          <div className="flex items-center gap-3">
            {/* Added more spacing between logo elements */}
            <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-lg">
              <Sparkles className="w-6 h-6 text-primary-foreground" />
            </div>
            <span className="text-xl font-semibold text-foreground">LeadForge</span>
          </div>
        </div>
      </div>
    </nav>
  );
}


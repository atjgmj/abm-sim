import React, { useState, useRef, useEffect } from 'react';
import { HelpCircle } from 'lucide-react';

interface TooltipProps {
  content: string;
  children?: React.ReactNode;
  showIcon?: boolean;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

export const Tooltip: React.FC<TooltipProps> = ({ 
  content, 
  children, 
  showIcon = true,
  position = 'top',
  className = ''
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isVisible && triggerRef.current && tooltipRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect();
      const tooltipRect = tooltipRef.current.getBoundingClientRect();
      
      let x = 0;
      let y = 0;

      switch (position) {
        case 'top':
          x = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2;
          y = triggerRect.top - tooltipRect.height - 8;
          break;
        case 'bottom':
          x = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2;
          y = triggerRect.bottom + 8;
          break;
        case 'left':
          x = triggerRect.left - tooltipRect.width - 8;
          y = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2;
          break;
        case 'right':
          x = triggerRect.right + 8;
          y = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2;
          break;
      }

      // Ensure tooltip stays within viewport
      x = Math.max(8, Math.min(x, window.innerWidth - tooltipRect.width - 8));
      y = Math.max(8, Math.min(y, window.innerHeight - tooltipRect.height - 8));

      setTooltipPosition({ x, y });
    }
  }, [isVisible, position]);

  return (
    <div className="relative inline-flex items-center">
      <div
        ref={triggerRef}
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        className={`cursor-help ${className}`}
      >
        {children || (showIcon && <HelpCircle className="h-4 w-4 text-gray-400 hover:text-gray-600" />)}
      </div>

      {isVisible && (
        <>
          {/* Backdrop to catch mouse events */}
          <div className="fixed inset-0 z-40 pointer-events-none" />
          
          {/* Tooltip */}
          <div
            ref={tooltipRef}
            className="fixed z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg max-w-xs"
            style={{
              left: tooltipPosition.x,
              top: tooltipPosition.y,
            }}
          >
            <div className="whitespace-pre-wrap">{content}</div>
            
            {/* Arrow */}
            <div
              className={`absolute w-2 h-2 bg-gray-900 transform rotate-45 ${
                position === 'top' ? 'bottom-[-4px] left-1/2 -translate-x-1/2' :
                position === 'bottom' ? 'top-[-4px] left-1/2 -translate-x-1/2' :
                position === 'left' ? 'right-[-4px] top-1/2 -translate-y-1/2' :
                'left-[-4px] top-1/2 -translate-y-1/2'
              }`}
            />
          </div>
        </>
      )}
    </div>
  );
};

// Helper component for form fields with tooltips
interface FieldWithTooltipProps {
  label: string;
  tooltip: string;
  children: React.ReactNode;
  required?: boolean;
}

export const FieldWithTooltip: React.FC<FieldWithTooltipProps> = ({
  label,
  tooltip,
  children,
  required = false
}) => {
  return (
    <div>
      <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
        <span>
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </span>
        <Tooltip content={tooltip} position="right" />
      </label>
      {children}
    </div>
  );
};
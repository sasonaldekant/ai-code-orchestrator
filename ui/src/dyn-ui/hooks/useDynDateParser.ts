/**
 * Date parsing hook for DYN UI DatePicker component
 * Part of DYN UI Form Components Group - SCOPE 6
 */

import { useState, useCallback } from 'react';

interface DateParserOptions {
  format?: string;
  locale?: string;
  customParser?: (input: string) => Date | null;
}

/**
 * Hook for date parsing with custom formats and locales
 * @param options - Date parser configuration
 * @returns Date parsing utilities
 */
export const useDynDateParser = ({
  format = 'dd/MM/yyyy',
  locale = 'pt-BR',
  customParser
}: DateParserOptions = {}) => {
  // Locale support is reserved for future enhancements; consume the value to satisfy linting.
  void locale;

  const [displayValue, setDisplayValue] = useState<string>('');

  const formatDate = useCallback((date: Date | null, formatStr: string = format): string => {
    if (!date) return '';

    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear().toString();

    return formatStr
      .replace('dd', day)
      .replace('MM', month)
      .replace('yyyy', year);
  }, [format]);

  const parseDate = useCallback((dateStr: string): Date | null => {
    if (!dateStr || dateStr.trim() === '') return null;

    // Try custom parser first
    if (customParser) {
      try {
        return customParser(dateStr);
      } catch {
        // Fall back to default parsing if custom parser fails
      }
    }

    // Handle natural language inputs (Portuguese)
    const today = new Date();
    const normalizedInput = dateStr.toLowerCase().trim();

    switch (normalizedInput) {
      case 'hoje':
      case 'today':
        return today;
      
      case 'ontem':
      case 'yesterday':
        const yesterday = new Date(today);
        yesterday.setDate(today.getDate() - 1);
        return yesterday;
      
      case 'amanhã':
      case 'amanha':
      case 'tomorrow':
        const tomorrow = new Date(today);
        tomorrow.setDate(today.getDate() + 1);
        return tomorrow;
    }

    // Try to parse standard formats
    const cleanStr = dateStr.replace(/[^0-9]/g, '');
    
    if (cleanStr.length === 8) {
      // DDMMYYYY format
      const day = parseInt(cleanStr.substr(0, 2));
      const month = parseInt(cleanStr.substr(2, 2)) - 1; // Month is 0-indexed
      const year = parseInt(cleanStr.substr(4, 4));

      if (day >= 1 && day <= 31 && month >= 0 && month <= 11 && year >= 1900) {
        const date = new Date(year, month, day);
        // Validate the date is actually valid (handles things like Feb 30th)
        if (
          date.getDate() === day &&
          date.getMonth() === month &&
          date.getFullYear() === year
        ) {
          return date;
        }
      }
    } else if (cleanStr.length === 6) {
      // DDMMYY format
      const day = parseInt(cleanStr.substr(0, 2));
      const month = parseInt(cleanStr.substr(2, 2)) - 1;
      let year = parseInt(cleanStr.substr(4, 2));
      
      // Handle 2-digit year (assume 20XX for years 00-30, 19XX for 31-99)
      year = year <= 30 ? 2000 + year : 1900 + year;

      if (day >= 1 && day <= 31 && month >= 0 && month <= 11) {
        const date = new Date(year, month, day);
        if (
          date.getDate() === day &&
          date.getMonth() === month &&
          date.getFullYear() === year
        ) {
          return date;
        }
      }
    }

    // Try standard date parsing as last resort
    try {
      const parsed = new Date(dateStr);
      if (!isNaN(parsed.getTime())) {
        return parsed;
      }
    } catch {
      // Ignore parsing errors
    }

    return null;
  }, [customParser]);

  const isValidDate = useCallback((date: Date | null): boolean => {
    return date !== null && date instanceof Date && !isNaN(date.getTime());
  }, []);

  const getRelativeDescription = useCallback((date: Date | null): string | null => {
    if (!date) return null;

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const targetDate = new Date(date);
    targetDate.setHours(0, 0, 0, 0);
    
    const diffTime = targetDate.getTime() - today.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'hoje';
    if (diffDays === 1) return 'amanhã';
    if (diffDays === -1) return 'ontem';
    if (diffDays > 1 && diffDays <= 7) return `em ${diffDays} dias`;
    if (diffDays < -1 && diffDays >= -7) return `${Math.abs(diffDays)} dias atrás`;

    return null;
  }, []);

  return {
    displayValue,
    setDisplayValue,
    formatDate,
    parseDate,
    isValidDate,
    getRelativeDescription
  };
};

/**
 * Predefined date formats
 */
export const DATE_FORMATS = {
  'pt-BR': 'dd/MM/yyyy',
  'en-US': 'MM/dd/yyyy',
  'ISO': 'yyyy-MM-dd',
  'short': 'dd/MM/yy',
  'long': 'dd de MMMM de yyyy'
} as const;

/**
 * Get date format by locale
 * @param locale - Locale string
 * @returns Date format pattern
 */
export const getDateFormat = (locale: keyof typeof DATE_FORMATS = 'pt-BR'): string => {
  return DATE_FORMATS[locale] || DATE_FORMATS['pt-BR'];
};

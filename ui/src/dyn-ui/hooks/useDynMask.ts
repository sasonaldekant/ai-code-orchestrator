/**
 * Input masking hook for DYN UI input components
 * Part of DYN UI Form Components Group - SCOPE 6
 */

import { useState, useCallback } from 'react';

interface MaskOptions {
  mask?: string;
  formatModel?: boolean;
}

/**
 * Hook for input masking functionality
 * @param mask - Mask pattern (e.g., "(##) ####-####" for phone)
 * @param initialValue - Initial value
 * @param formatModel - Whether to format the model value
 * @returns Masked value, unmasked value, and change handler
 */
export const useDynMask = (
  mask?: string,
  initialValue: string = '',
  formatModel: boolean = false
) => {
  const [maskedValue, setMaskedValue] = useState<string>(
    mask ? applyMask(initialValue, mask) : initialValue
  );

  const unmaskValue = useCallback((value: string): string => {
    if (!mask) return value;
    return value.replace(/[^0-9a-zA-Z]/g, '');
  }, [mask]);

  const handleMaskedChange = useCallback((newValue: string): string => {
    if (!mask) return newValue;
    
    const maskedResult = applyMask(newValue, mask);
    setMaskedValue(maskedResult);
    
    return formatModel ? maskedResult : unmaskValue(maskedResult);
  }, [mask, formatModel, unmaskValue]);

  return {
    maskedValue,
    unmaskValue,
    handleMaskedChange
  };
};

/**
 * Apply mask to a value
 * @param value - Input value
 * @param mask - Mask pattern
 * @returns Masked value
 */
function applyMask(value: string, mask: string): string {
  if (!mask || !value) return value;

  const cleanValue = value.replace(/[^0-9a-zA-Z]/g, '');
  let maskedValue = '';
  let valueIndex = 0;

  for (let i = 0; i < mask.length && valueIndex < cleanValue.length; i++) {
    const maskChar = mask[i];
    
    if (maskChar === '#') {
      // Numeric placeholder
      if (/[0-9]/.test(cleanValue[valueIndex])) {
        maskedValue += cleanValue[valueIndex];
        valueIndex++;
      } else {
        break;
      }
    } else if (maskChar === 'A') {
      // Alpha placeholder
      if (/[a-zA-Z]/.test(cleanValue[valueIndex])) {
        maskedValue += cleanValue[valueIndex];
        valueIndex++;
      } else {
        break;
      }
    } else if (maskChar === '*') {
      // Alphanumeric placeholder
      maskedValue += cleanValue[valueIndex];
      valueIndex++;
    } else {
      // Literal character
      maskedValue += maskChar;
    }
  }

  return maskedValue;
}

/**
 * Predefined mask patterns
 */
export const MASK_PATTERNS = {
  phone: '(##) ####-####',
  phoneWithCountry: '+## (##) ####-####',
  cpf: '###.###.###-##',
  cnpj: '##.###.###/####-##',
  cep: '#####-###',
  creditCard: '#### #### #### ####',
  date: '##/##/####',
  time: '##:##',
  currency: '###.###.###,##'
} as const;

/**
 * Get mask pattern by type
 * @param type - Mask type
 * @returns Mask pattern
 */
export const getMaskPattern = (type: keyof typeof MASK_PATTERNS): string => {
  return MASK_PATTERNS[type];
};
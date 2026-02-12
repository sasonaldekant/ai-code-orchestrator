import { useState, useCallback, useEffect } from 'react';

export type ValidationRuleType =
  | 'required'
  | 'email'
  | 'url'
  | 'pattern'
  | 'minLength'
  | 'maxLength'
  | 'min'
  | 'max'
  | 'number'
  | 'custom';

export interface ValidationRule {
  type: ValidationRuleType;
  message: string;
  value?: any;
  validator?: (value: any) => boolean | string | Promise<boolean | string>;
}

export type DynValidationRule = ValidationRule | ((value: any) => string | boolean | null | undefined | Promise<string | boolean | null | undefined>);

interface UseFieldValidationOptions {
  value: any;
  required?: boolean;
  validation?: DynValidationRule | DynValidationRule[];
  customError?: string;
}

/**
 * Modernized Validation Hook
 * Supports both object-style rules and function-style rules.
 */
export const useDynFieldValidation = ({
  value,
  required,
  validation,
  customError
}: UseFieldValidationOptions) => {
  const [error, setError] = useState<string>(customError || '');

  // Immediately sync customError to state when it changes
  useEffect(() => {
    if (customError !== undefined) {
      setError(customError);
    }
  }, [customError]);

  const validate = useCallback(async (): Promise<boolean> => {
    setError('');

    if (customError) {
      setError(customError);
      return false;
    }

    if (required) {
      if (
        value === undefined ||
        value === null ||
        value === '' ||
        (Array.isArray(value) && value.length === 0)
      ) {
        setError('Field is required'); // Standardized English message
        return false;
      }
    }

    if (validation) {
      const rules = Array.isArray(validation) ? validation : [validation];

      for (const rule of rules) {
        let isValid = true;
        let errorMessage = '';

        if (typeof rule === 'function') {
          const result = await rule(value);
          if (typeof result === 'string') {
            isValid = false;
            errorMessage = result;
          } else if (result === false) {
            isValid = false;
            errorMessage = 'Invalid value';
          }
        } else {
          errorMessage = rule.message;
          switch (rule.type) {
            case 'minLength':
              if (typeof rule.value === 'number' && String(value).length < rule.value) {
                isValid = false;
              }
              break;
            case 'maxLength':
              if (typeof rule.value === 'number' && String(value).length > rule.value) {
                isValid = false;
              }
              break;
            case 'number':
              if (value !== '' && (isNaN(Number(value)) || /^\s*$/.test(String(value)))) {
                isValid = false;
              }
              break;
            case 'min':
              if (value !== '' && !isNaN(Number(value)) && Number(value) < Number(rule.value)) {
                isValid = false;
              }
              break;
            case 'max':
              if (value !== '' && !isNaN(Number(value)) && Number(value) > Number(rule.value)) {
                isValid = false;
              }
              break;
            case 'email':
              const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
              if (value !== '' && !emailRegex.test(String(value))) {
                isValid = false;
              }
              break;
            case 'url':
              if (value !== '') {
                try {
                  new URL(String(value));
                } catch {
                  isValid = false;
                }
              }
              break;
            case 'pattern':
              const regex = typeof rule.value === 'string' ? new RegExp(rule.value) : rule.value;
              if (regex && value !== '' && !regex.test(String(value))) {
                isValid = false;
              }
              break;
            case 'custom':
              if (rule.validator) {
                const result = await rule.validator(value);
                if (typeof result === 'string') {
                  isValid = false;
                  errorMessage = result;
                } else {
                  isValid = result;
                }
              }
              break;
          }
        }

        if (!isValid) {
          setError(errorMessage);
          return false;
        }
      }
    }

    return true;
  }, [value, required, validation, customError]);

  const clearError = useCallback(() => {
    setError('');
  }, []);

  return {
    error,
    isValid: !error,
    validate,
    clearError
  };
};

export default useDynFieldValidation;

import { useContext } from 'react';
import { IconDictionaryContext } from '../providers/IconDictionaryProvider';

export const useIconDictionary = () => {
  const context = useContext(IconDictionaryContext);
  
  if (!context) {
    throw new Error('useIconDictionary must be used within IconDictionaryProvider');
  }
  
  return context;
};

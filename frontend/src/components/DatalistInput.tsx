import React from 'react';
import { useTranslation } from 'react-i18next';

interface DatalistInputProps<T extends string> {
  id: string;
  value: T | undefined;
  onChange: (value: T | undefined) => void;
  placeholder: string;
  options: readonly T[];
  optionTranslationKey: string;
  required?: boolean;
}

function DatalistInput<T extends string>({
  id,
  value,
  onChange,
  placeholder,
  options,
  optionTranslationKey,
  required = false,
}: DatalistInputProps<T>) {
  const { t } = useTranslation();

  // Create mapping from translated values back to keys
  const translationToKey = React.useMemo(() => {
    const map = new Map<string, T>();
    options.forEach((option) => {
      const translation = t(`${optionTranslationKey}.${option}`);
      map.set(translation, option);
    });
    return map;
  }, [options, optionTranslationKey, t]);

  // Create mapping from keys to translated values
  const keyToTranslation = React.useMemo(() => {
    const map = new Map<T, string>();
    options.forEach((option) => {
      const translation = t(`${optionTranslationKey}.${option}`);
      map.set(option, translation);
    });
    return map;
  }, [options, optionTranslationKey, t]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    if (inputValue === '') {
      onChange(undefined);
    } else {
      // Check if the input value is a translated option
      const keyFromTranslation = translationToKey.get(inputValue);
      if (keyFromTranslation) {
        onChange(keyFromTranslation);
      } else if (options.includes(inputValue as T)) {
        // Direct key match
        onChange(inputValue as T);
      } else {
        // Allow custom values that aren't in the predefined options
        onChange(inputValue as T);
      }
    }
  };

  // Display the translated value in the input
  const displayValue = value ? (keyToTranslation.get(value) || value) : "";

  return (
    <>
      <input
        type="text"
        id={id}
        list={`${id}-options`}
        value={displayValue}
        onChange={handleChange}
        placeholder={placeholder}
        required={required}
      />
      <datalist id={`${id}-options`}>
        {options.map((option) => {
          const translation = t(`${optionTranslationKey}.${option}`);
          return (
            <option key={option} value={translation}>
              {translation}
            </option>
          );
        })}
      </datalist>
    </>
  );
}

export default DatalistInput;

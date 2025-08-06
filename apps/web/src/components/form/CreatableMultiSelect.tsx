import React from 'react';
import CreatableSelect from 'react-select/creatable';

interface Option {
  readonly label: string;
  readonly value: string;
}

interface CreatableMultiSelectProps {
  options: Option[];
  value: Option[];
  onChange: (value: readonly Option[]) => void;
  onCreateOption: (inputValue: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}

const CreatableMultiSelect: React.FC<CreatableMultiSelectProps> = ({
  options,
  value,
  onChange,
  onCreateOption,
  isLoading = false,
  placeholder = 'Select or create...',
}) => {
  return (
    <CreatableSelect
      isMulti
      isClearable
      options={options}
      value={value}
      onChange={onChange}
      onCreateOption={onCreateOption}
      isLoading={isLoading}
      placeholder={placeholder}
      className='text-black'
      // You can further customize styles here using the `styles` prop
      // and Tailwind CSS classes via the `className` and `classNamePrefix` props
      // For example:
      // classNamePrefix="react-select"
    />
  );
};

export default CreatableMultiSelect;

import React from 'react';
import { WithContext as ReactTagInput, Tag } from 'react-tag-input';
import { X } from 'lucide-react';

// You might need to create a separate CSS file for styling
// For now, we'll rely on default or inline styles.

interface TagInputProps {
  tags: Tag[];
  setTags: (tags: Tag[]) => void;
  placeholder: string;
}

const KeyCodes = {
  comma: 188,
  enter: 13,
  space: 32,
};

const delimiters = [KeyCodes.comma, KeyCodes.enter, KeyCodes.space];

const TagInput: React.FC<TagInputProps> = ({ tags, setTags, placeholder }) => {
  const handleDelete = (i: number) => {
    setTags(tags.filter((tag, index) => index !== i));
  };

  const handleAddition = (tag: Tag) => {
    setTags([...tags, tag]);
  };

  const handleDrag = (tag: Tag, currPos: number, newPos: number) => {
    const newTags = [...tags];
    newTags.splice(currPos, 1);
    newTags.splice(newPos, 0, tag);
    setTags(newTags);
  };

  // Basic styling for the component
  // A proper implementation would use Tailwind and a dedicated CSS module
  const tagInputStyle = {
    tags: {
      display: 'flex',
      flexWrap: 'wrap' as 'wrap',
      gap: '5px',
    },
    tag: {
      background: '#eee',
      padding: '5px 8px',
      borderRadius: '5px',
      display: 'flex',
      alignItems: 'center',
      gap: '5px',
    },
    remove: {
      cursor: 'pointer',
    },
    tagInputField: {
      width: '100%',
      padding: '8px',
      border: '1px solid #ccc',
      borderRadius: '4px',
      marginTop: '10px',
    },
  };

  return (
    <div>
      <ReactTagInput
        tags={tags}
        handleDelete={handleDelete}
        handleAddition={handleAddition}
        handleDrag={handleDrag}
        delimiters={delimiters}
        inputFieldPosition="bottom"
        autocomplete
        placeholder={placeholder}
        classNames={{
          tags: 'flex flex-wrap gap-2 text-gray-800',
          tag: 'bg-gray-200 text-gray-800 text-sm font-medium me-2 px-2.5 py-0.5 rounded flex items-center gap-1',
          remove: 'cursor-pointer',
          tagInputField: 'mt-2 w-full p-2 border border-gray-300 rounded',
        }}
      />
    </div>
  );
};

export default TagInput;

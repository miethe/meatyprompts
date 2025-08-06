import React, { useState } from 'react';
import { useLookups } from '@/contexts/LookupContext';
import { usePrompt } from '@/contexts/PromptContext';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '../ui/sheet';
import { Button } from '../ui/button';
import CreatableMultiSelect from '../form/CreatableMultiSelect';

interface Option {
  value: string;
  label: string;
}

const PromptListFilters: React.FC = () => {
  const { lookups } = useLookups();
  const { filterPrompts } = usePrompt(); // Assuming usePrompt returns a filter function

  const [modelFilter, setModelFilter] = useState<readonly Option[]>([]);
  const [toolFilter, setToolFilter] = useState<readonly Option[]>([]);
  const [purposeFilter, setPurposeFilter] = useState<readonly Option[]>([]);

  const handleApplyFilters = () => {
    const filters = {
      model: modelFilter.length > 0 ? modelFilter[0].value : undefined,
      tool: toolFilter.length > 0 ? toolFilter[0].value : undefined,
      purpose: purposeFilter.length > 0 ? purposeFilter[0].value : undefined,
    };
    // filterPrompts(filters);
    console.log("Applying filters:", filters);
  };

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline">Filters</Button>
      </SheetTrigger>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Filter Prompts</SheetTitle>
        </SheetHeader>
        <div className="grid gap-4 py-4">
          <div className="flex flex-col gap-2">
            <label>Models</label>
            <CreatableMultiSelect
              isMulti={false} // Allow filtering by one model at a time for simplicity
              isLoading={lookups.loading}
              options={lookups.models}
              value={modelFilter}
              onChange={setModelFilter}
              placeholder="Filter by model..."
            />
          </div>
          <div className="flex flex-col gap-2">
            <label>Tools</label>
            <CreatableMultiSelect
              isMulti={false}
              isLoading={lookups.loading}
              options={lookups.tools}
              value={toolFilter}
              onChange={setToolFilter}
              placeholder="Filter by tool..."
            />
          </div>
          <div className="flex flex-col gap-2">
            <label>Purpose</label>
            <CreatableMultiSelect
              isMulti={false}
              isLoading={lookups.loading}
              options={lookups.purposes}
              value={purposeFilter}
              onChange={setPurposeFilter}
              placeholder="Filter by purpose..."
            />
          </div>
        </div>
        <Button onClick={handleApplyFilters} className="w-full">Apply Filters</Button>
      </SheetContent>
    </Sheet>
  );
};

export default PromptListFilters;

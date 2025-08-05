import React, { useState } from 'react';
import NewPromptButton from '@/components/NewPromptButton';
import PromptWizard from '@/components/modals/PromptWizard';

const DashboardPage = () => {
  const [isWizardOpen, setIsWizardOpen] = useState(false);

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <NewPromptButton onClick={() => setIsWizardOpen(true)} />
      </div>
      <p className="mt-4">Welcome to your dashboard.</p>
      {isWizardOpen && <PromptWizard onClose={() => setIsWizardOpen(false)} />}
    </div>
  );
};

export default DashboardPage;

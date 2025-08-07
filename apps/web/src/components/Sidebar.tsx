import React, { useState } from 'react';
import Link from 'next/link';
import { useTranslation } from 'react-i18next';
import { Plus } from 'lucide-react';
import ThemedButton from './common/ThemedButton';
import NewPromptModal from './modals/NewPromptModal';

const Sidebar = () => {
  const [modalOpen, setModalOpen] = useState(false);
  const { t } = useTranslation();

  return (
    <div className="flex flex-col w-64 bg-gray-800">
      <div className="flex items-center justify-center h-16 bg-gray-900">
        <span className="text-white font-bold uppercase">MeatyPrompts</span>
      </div>
      <div className="flex flex-col flex-grow p-4">
        <nav>
          <ul>
            <li>
              <Link href="/dashboard" className="flex items-center h-10 px-3 text-gray-300 rounded hover:bg-gray-700">
                <span className="mr-2">📊</span>
                {!isCollapsed && t('sidebar.dashboard', 'Dashboard')}
                Dashboard
              </Link>
            </li>
            <li>
              <Link href="/prompts" className="flex items-center h-10 px-3 text-gray-300 rounded hover:bg-gray-700">
                <span className="mr-2">💡</span>
                {!isCollapsed && t('sidebar.prompts', 'Prompts')}
                Prompts
              </Link>
            </li>
          </ul>
        </nav>
      </div>
      <div className="flex flex-col items-center p-4">
        <ThemedButton
          label="New Prompt"
          Icon={Plus}
          onClick={() => setModalOpen(true)}
        />
      </div>
      {modalOpen && <NewPromptModal onClose={() => setModalOpen(false)} />}
    </div>
  );
};

export default Sidebar;

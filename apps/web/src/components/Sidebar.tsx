import React, { useState } from 'react';
import Link from 'next/link';
import { useTranslation } from 'react-i18next';
import { Plus } from 'lucide-react';
import ThemedButton from './common/ThemedButton';
import NewPromptModal from './modals/NewPromptModal';

const Sidebar = () => {
  const [modalOpen, setModalOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { t } = useTranslation();

  return (
     <div className={`flex flex-col bg-gray-800 ${isCollapsed ? 'w-20' : 'w-64'} transition-all duration-300`}>
      <div className="flex items-center justify-center h-16 bg-gray-900">
        <span className="text-white font-bold uppercase">{isCollapsed ? 'MP' : 'MeatyPrompts'}</span>
      </div>
      <div className="flex flex-col flex-grow p-4">
        <nav>
          <ul>
            <li>
              <Link href="/dashboard" className="flex items-center h-10 px-3 text-gray-300 rounded hover:bg-gray-700">
                <span className="mr-2">📊</span>
                {!isCollapsed && t('sidebar.dashboard', 'Dashboard')}
              </Link>
            </li>
            <li>
              <Link href="/prompts" className="flex items-center h-10 px-3 text-gray-300 rounded hover:bg-gray-700">
                <span className="mr-2">💡</span>
                {!isCollapsed && t('sidebar.prompts', 'Prompts')}
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
      <button
        className="flex items-center justify-center h-10 text-gray-300 bg-gray-900 hover:bg-gray-700"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        {isCollapsed ? '→' : '←'}
      </button>
      {modalOpen && <NewPromptModal onClose={() => setModalOpen(false)} />}
    </div>
  );
};

export default Sidebar;

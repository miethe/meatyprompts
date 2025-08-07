import React from 'react';
import Link from 'next/link';
import { Plus } from 'lucide-react';
import { useRouter } from 'next/router';
import ThemedButton from './common/ThemedButton';

const Sidebar = () => {
  const router = useRouter();

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
                Dashboard
              </Link>
            </li>
            <li>
              <Link href="/prompts" className="flex items-center h-10 px-3 text-gray-300 rounded hover:bg-gray-700">
                <span className="mr-2">💡</span>
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
          onClick={() => router.push('/prompts/new')}
        />
      </div>
    </div>
  );
};

export default Sidebar;

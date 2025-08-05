import React, { useState } from 'react';
import Link from 'next/link';

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div className={`flex flex-col bg-gray-800 ${isCollapsed ? 'w-20' : 'w-64'} transition-all duration-300`}>
      <div className="flex items-center justify-center h-16 bg-gray-900">
        <span className="text-white font-bold uppercase">{isCollapsed ? 'MP' : 'MeatyPrompts'}</span>
      </div>
      <div className="flex flex-col flex-grow p-4">
        <nav>
          <ul>
            <li>
              <Link href="/dashboard">
                <a className="flex items-center h-10 px-3 text-gray-300 rounded hover:bg-gray-700">
                  <span className="mr-2">📊</span>
                  {!isCollapsed && 'Dashboard'}
                </a>
              </Link>
            </li>
            <li>
              <Link href="/prompts">
                <a className="flex items-center h-10 px-3 text-gray-300 rounded hover:bg-gray-700">
                  <span className="mr-2">💡</span>
                  {!isCollapsed && 'Prompts'}
                </a>
              </Link>
            </li>
          </ul>
        </nav>
      </div>
      <button
        className="flex items-center justify-center h-10 text-gray-300 bg-gray-900 hover:bg-gray-700"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        {isCollapsed ? '→' : '←'}
      </button>
    </div>
  );
};

export default Sidebar;

import React, { ReactNode } from 'react';
import Sidebar from './Sidebar';
import NotLoggedInAlert from './NotLoggedInAlert';

const Layout = ({ children }: { children: ReactNode }) => {
  return (
    <div className="flex h-screen bg-blend-darken">
      <Sidebar />
      <div className="flex-grow p-6">{children}</div>
      <NotLoggedInAlert />
    </div>
  );
};

export default Layout;

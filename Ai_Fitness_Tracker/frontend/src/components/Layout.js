import React from 'react';
import { Outlet } from 'react-router-dom';
import BottomNav from './BottomNav';

const Layout = () => {
  return (
    <div className="min-h-screen bg-white dark:bg-black pb-20 transition-colors duration-300">
      <Outlet />
      <BottomNav />
    </div>
  );
};

export default Layout;

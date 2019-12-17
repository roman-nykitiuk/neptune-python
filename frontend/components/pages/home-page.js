import React from 'react';
import Loadable from 'react-loadable';
import AdminContainer from '@/containers/admin-container';

const HomePage = () => {
  const DashboardContainer = Loadable({
    loader: () => import('@/containers/dashboard-container'),
    loading: () => null,
  });

  return (
    <AdminContainer>
      <DashboardContainer />
    </AdminContainer>
  );
};

export default HomePage;

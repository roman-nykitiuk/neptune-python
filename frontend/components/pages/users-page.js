import React from 'react';
import Loadable from 'react-loadable';
import AdminContainer from '@/containers/admin-container';

const HomePage = () => {
  const UsersContainer = Loadable({
    loader: () => import('@/containers/users-container'),
    loading: () => null,
  });

  return (
    <AdminContainer>
      <UsersContainer />
    </AdminContainer>
  );
};

export default HomePage;

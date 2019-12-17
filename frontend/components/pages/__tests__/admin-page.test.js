import React from 'react';
import AdminPage from '@/components/pages/admin-page';
import { Body } from '@/components/pages/admin-styles';

describe('AdminPage', () => {
  let props;
  let wrapper;
  const FakeNode = () => 'AdminPage';

  describe('Authenticated', () => {
    beforeEach(() => {
      props = { isAuthenticated: true, user: { name: 'Admin' } };
      wrapper = shallow(
        <AdminPage {...props}>
          <FakeNode />
        </AdminPage>,
      );
    });

    it('should render Header', () => {
      const header = wrapper.find('Header');
      expect(header.length).toEqual(1);
      expect(header.props().user).toEqual(props.user);
    });

    it('should render children', () => {
      expect(wrapper.find(Body).find(FakeNode).length).toEqual(1);
    });
  });

  describe('Unauthenticated', () => {
    beforeEach(() => {
      props = { isAuthenticated: false, user: {} };
      wrapper = shallow(
        <AdminPage {...props}>
          <FakeNode />
        </AdminPage>,
      );
    });

    it('should redirect to login page', () => {
      expect(wrapper.find('Redirect').length).toEqual(1);
    });
  });
});

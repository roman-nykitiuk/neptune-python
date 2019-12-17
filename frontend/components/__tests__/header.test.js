import React from 'react';
import Header from '@/components/header';
import { Navbar } from '@/components/header-styles';

describe('Header', () => {
  describe('render()', () => {
    it('should show user name in navigation bar', () => {
      const user = { name: 'Dr. Lusgarten' };
      const wrapper = shallow(<Header user={user} />);
      expect(wrapper.find(Navbar).length).toEqual(1);
      expect(wrapper.find('span').text()).toContain(user.name);
    });
  });
});

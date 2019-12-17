import React from 'react';
import Menu from '@/components/menu';
import { MenuItem } from '@/components/menu-styles';

describe('Menu', () => {
  const mockLogout = jest.fn();
  let wrapper;

  beforeEach(() => {
    wrapper = shallow(<Menu logout={mockLogout} />);
  });

  it('should render 7 menu items', () => {
    expect(wrapper.find(MenuItem).length).toEqual(7);
  });

  it('should call onLogoutClick', () => {
    wrapper.findWhere(item => item.key() === 'logout').simulate('click', { preventDefault: jest.fn() });
    expect(mockLogout.mock.calls.length).toBe(1);
  });
});

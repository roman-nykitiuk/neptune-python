import React from 'react';
import HomePage from '@/components/pages/home-page';
import AdminContainer from '@/containers/admin-container';

jest.mock('react-plotly.js', () => () => null);

describe('HomePage', () => {
  it('should render AdminContainer', () => {
    const wrapper = shallow(<HomePage />);
    expect(wrapper.find(AdminContainer).length).toEqual(1);
  });
});

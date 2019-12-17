import React from 'react';
import Repcase from '@/components/dashboard/repcase';

describe('Repcase', () => {
  it('should render a table', () => {
    const wrapper = mount(<Repcase />);
    expect(wrapper.find('table').length).toEqual(1);
  });
});

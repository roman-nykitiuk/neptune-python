import React from 'react';
import Spend from '@/components/dashboard/aggregation/spend';
import { Total, DownValue } from '@/components/dashboard/aggregation/aggregation-styles';

describe('Spend', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(<Spend total={100} currentMonth={10} />);
  });

  it('render Total', () => {
    const total = wrapper.find(Total);
    expect(total.length).toEqual(1);
    expect(total.text()).toEqual('$100');
  });

  it('render current month value', () => {
    const value = wrapper.find(DownValue);
    expect(value.length).toEqual(1);
    expect(value.text()).toEqual('10 this month');
  });
});

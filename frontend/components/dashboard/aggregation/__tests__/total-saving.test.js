import React from 'react';
import TotalSaving from '@/components/dashboard/aggregation/total-saving';
import { Total, UpValue } from '@/components/dashboard/aggregation/aggregation-styles';

describe('Spend', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(<TotalSaving total={200} currentMonth={20} />);
  });

  it('render Total', () => {
    const total = wrapper.find(Total);
    expect(total.length).toEqual(1);
    expect(total.text()).toEqual('$200');
  });

  it('render current month value', () => {
    const value = wrapper.find(UpValue);
    expect(value.length).toEqual(1);
    expect(value.text()).toEqual('20 from last month');
  });
});

import React from 'react';
import Aggregation from '@/components/dashboard/aggregation/aggregation';
import TotalSaving from '@/components/dashboard/aggregation/total-saving';
import BulkInventory from '@/components/dashboard/aggregation/bulk-inventory';
import Spend from '@/components/dashboard/aggregation/spend';

describe('Aggregation', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallow(<Aggregation />);
  });

  it('should render TotalSaving', () => {
    expect(wrapper.find(TotalSaving));
  });

  it('should render Spend', () => {
    expect(wrapper.find(Spend));
  });

  it('should render BulkInventory', () => {
    expect(wrapper.find(BulkInventory));
  });
});

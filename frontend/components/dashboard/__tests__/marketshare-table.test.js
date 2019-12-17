import React from 'react';
import MarketshareTable, { StyledTable } from '@/components/dashboard/marketshare-table';

describe('MarketshareTable', () => {
  it('should render a table', () => {
    const props = {
      marketshare: [
        { id: 1, name: 'BIO', spend: '100.00', units: 2 },
        { id: 2, name: 'MDT', spend: '300.00', units: 3 },
      ],
    };
    const wrapper = shallow(<MarketshareTable {...props} />);
    const table = wrapper.find(StyledTable);
    expect(table.length).toEqual(1);
    expect(table.props().rows).toEqual([
      { id: 1, name: 'BIO', spend: '$100', units: 2, marketshare: '25.0%' },
      { id: 2, name: 'MDT', spend: '$300', units: 3, marketshare: '75.0%' },
    ]);
  });
});

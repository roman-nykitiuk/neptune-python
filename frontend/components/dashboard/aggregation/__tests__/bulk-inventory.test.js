import React from 'react';
import BulkInventory from '@/components/dashboard/aggregation/bulk-inventory';

describe('BulkInventory', () => {
  let wrapper;
  let props;

  beforeEach(() => {
    props = {
      getBulkInventory: jest.fn(),
      bulkInventory: {
        expiring60: 20,
        expiring30: 30,
        expired: 10,
      },
      clientId: 1,
    };
    wrapper = shallow(<BulkInventory {...props} />);
  });

  it('should render item information', () => {
    const ps = wrapper.find('p');
    expect(ps.length).toEqual(3);
    expect(ps.at(0).text()).toEqual('20 Items Expiring');
    expect(ps.at(1).text()).toEqual('30 Items Low In Stock');
    expect(ps.at(2).text()).toEqual('10 Items Out Of Stock');
  });

  it('should call getBulkInventory after mounted', () => {
    expect(props.getBulkInventory).toHaveBeenCalled();
  });
});

import React from 'react';
import Plot from '@/react-plotly.js';
import MarketshareChart from '@/components/dashboard/marketshare-chart';

jest.mock('react-plotly.js', () => () => null);

describe('MarketshareChart', () => {
  it('should render a Plot', () => {
    const props = {
      marketshare: [
        { id: 1, name: 'BIO', spend: '100.00', units: 2 },
        { id: 2, name: 'MDT', spend: '200.00', units: 3 },
      ],
    };
    const wrapper = shallow(<MarketshareChart {...props} />);
    const plot = wrapper.find(Plot);
    expect(plot.length).toEqual(1);
    expect(plot.props().data[0].labels).toEqual(['BIO', 'MDT']);
    expect(plot.props().data[0].values).toEqual(['100.00', '200.00']);
    expect(plot.props().data[0].text).toEqual(['$100<br />2 units', '$200<br />3 units']);
  });
});

import React from 'react';
import Marketshare from '@/components/dashboard/marketshare';
import { Title } from '@/components/dashboard/dashboard-styles';
import MarketshareChart from '@/components/dashboard/marketshare-chart';
import MarketshareTable from '@/components/dashboard/marketshare-table';

jest.mock('react-plotly.js', () => () => null);

describe('Marketshare', () => {
  let wrapper;
  let props;

  beforeEach(() => {
    props = {
      getMarketShare: jest.fn(),
      clientId: 1,
      marketshare: {
        marketshare: [{ id: 1, name: 'BIO', spend: '100', units: 10 }],
        name: '2018',
      },
    };
    wrapper = mount(<Marketshare {...props} />);
  });

  it('should render MarketshareChart', () => {
    const marketshareChart = wrapper.find(MarketshareChart);
    expect(marketshareChart.length).toEqual(1);
    expect(marketshareChart.props().marketshare).toEqual(props.marketshare.marketshare);
  });

  it('should render title', () => {
    const title = wrapper.find(Title);
    expect(title.length).toEqual(1);
    expect(title.text()).toEqual('2018 Market Share');
  });

  it('should render MarketshareTable when marketshare is not an empty array', () => {
    const marketshareTable = wrapper.find(MarketshareTable);
    expect(marketshareTable.length).toEqual(1);
    expect(marketshareTable.props().marketshare).toEqual(props.marketshare.marketshare);
  });

  it('should render no data when marketshare is empty', () => {
    props = {
      getMarketShare: jest.fn(),
      clientId: 1,
      marketshare: { marketshare: [], name: '2018' },
    };
    wrapper = render(<Marketshare {...props} />);
    const span = wrapper.find('p');
    expect(span.length).toEqual(1);
    expect(span.text()).toEqual('No data found');
  });

  it('should call getMarketShare after mounting', () => {
    expect(props.getMarketShare).toHaveBeenCalled();
  });
});

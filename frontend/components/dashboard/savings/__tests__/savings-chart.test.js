import React from 'react';
import Plot from '@/react-plotly.js';
import SavingsChart from '../savings-chart';

jest.mock('@/react-plotly.js', () => () => null);

describe('SavingsChart', () => {
  let wrapper;
  let props;

  beforeEach(() => {
    props = {
      savings: [
        { month: 1, savings: '100.00', percentOfSum: 20, percent: '0', spend: '0' },
        { month: 2, savings: '400.00', percentOfSum: 80, percent: '0', spend: '0' },
      ],
      filter: 'savings',
    };
    wrapper = shallow(<SavingsChart {...props} />);
  });

  it('should render Plot component', () => {
    const plot = wrapper.find(Plot);
    expect(plot.length).toEqual(1);
    const data = plot.props().data[0];
    expect(data.y).toEqual(['100.00', '400.00', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]);
    expect(data.marker).toEqual({
      color: [
        '#8eb2dd',
        '#496b92',
        '#8eb2dd',
        '#8eb2dd',
        '#8eb2dd',
        '#8eb2dd',
        '#8eb2dd',
        '#8eb2dd',
        '#8eb2dd',
        '#8eb2dd',
        '#8eb2dd',
        '#8eb2dd',
      ],
    });
  });
});

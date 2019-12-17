import React from 'react';
import { Title } from '@/components/dashboard/dashboard-styles';
import Savings, { SavingsTable } from '../savings';
import SavingsChart from '../savings-chart';

jest.mock('react-plotly.js', () => () => null);

describe('Analytic', () => {
  const mockUpdateChartFilter = jest.fn();
  let wrapper;
  let props;

  beforeEach(() => {
    global.Date = jest.fn(() => ({
      getMonth: jest.fn().mockReturnValue(1),
    }));
    global.Date.now = jest.fn(() => ({
      getMonth: jest.fn().mockReturnValue(1),
    }));
    props = {
      getSavings: jest.fn(),
      clientId: 1,
      savings: {
        data: [
          { month: 1, savings: '100.00', percent: '0', spend: '0' },
          { month: 2, savings: '400.00', percent: '0', spend: '0' },
        ],
        filter: 'savings',
      },
      filters: ['savings', 'spend'],
      updateChartFilter: mockUpdateChartFilter,
    };
    wrapper = mount(<Savings {...props} />);
  });

  it('should render title', () => {
    expect(wrapper.find(Title).text()).toEqual('Net savings');
  });

  it('should render SavingsTable', () => {
    const savingsTable = wrapper.find(SavingsTable);
    const trs = savingsTable.find('tr');
    expect(savingsTable.length).toEqual(1);
    expect(trs.length).toEqual(2);
    expect(trs.at(0).text()).toContain('February savings$400');
    expect(trs.at(1).text()).toContain('Year to Date savings$500');
  });

  it('should render SavingsChart', () => {
    const savingsChart = wrapper.find(SavingsChart);
    expect(savingsChart.length).toEqual(1);
    expect(savingsChart.props().savings).toEqual([
      { month: 1, savings: '100.00', percentOfSum: 20, percent: '0', spend: '0' },
      { month: 2, savings: '400.00', percentOfSum: 80, percent: '0', spend: '0' },
    ]);
  });

  it('should re-render Chart when change filter', () => {
    const selectFilter = wrapper.find('select').first();
    expect(selectFilter.length).toEqual(1);

    selectFilter.simulate('change', { target: { value: 'spending' } });
    expect(mockUpdateChartFilter.mock.calls.length).toBe(1);
  });
});

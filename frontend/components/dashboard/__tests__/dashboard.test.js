import React from 'react';
import Dashboard from '@/components/dashboard/dashboard';
import MarketShareContainer from '@/containers/dashboard/marketshare-container';
import RepCaseContainer from '@/containers/dashboard/rep-case-container';
import SavingsContainer from '@/containers/dashboard/savings-container';

jest.mock('react-plotly.js', () => () => null);

describe('Dashboard', () => {
  let props;
  let wrapper;

  describe('Authenticated', () => {
    beforeEach(() => {
      props = { clientId: 1 };
      wrapper = shallow(<Dashboard {...props} />);
    });

    it('should render RepCaseContainer', () => {
      expect(wrapper.find(RepCaseContainer).length).toEqual(1);
    });

    it('should render Aggregration section', () => {
      expect(wrapper.find('Aggregation').length).toEqual(1);
    });

    it('should render MarketShareContainer', () => {
      expect(wrapper.find(MarketShareContainer).length).toEqual(1);
    });

    it('should render SavingsContainer', () => {
      expect(wrapper.find(SavingsContainer).length).toEqual(1);
    });
  });
});

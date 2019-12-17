import * as types from '@/constants/action-types';
import getSavings, { updateChartFilter } from '../savings-actions';

describe('getSavings', () => {
  const mock = getMockAxios();
  const store = getMockStore();

  beforeEach(() => {
    store.clearActions();
  });

  afterEach(() => {
    mock.reset();
  });

  describe('savings success', () => {
    const savings = [{ month: 1, savings: '100.00' }, { month: 3, savings: '200.00' }];
    beforeEach(() => {
      mock.onGet('/api/admin/clients/8/savings').reply(200, savings);
    });

    it('should dispatch REP_CASE_SUCCESS', () =>
      store.dispatch(getSavings(8)).then(() => {
        expect(store.getActions()).toEqual([
          {
            type: types.SAVINGS_SUCCESS,
            savings,
          },
        ]);
      }));
  });

  describe('select filter change', () => {
    const filter = 'savings';

    it('should dispatch SAVINGS_UPDATE_CHART_FILTER', () => {
      const expectedAction = {
        type: types.SAVINGS_UPDATE_CHART_FILTER,
        filter,
      };
      expect(updateChartFilter(filter)).toEqual(expectedAction);
    });
  });
});

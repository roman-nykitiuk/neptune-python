import * as types from '@/constants/action-types';
import reducer from '../savings';

describe('savings reducer', () => {
  it('should return initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      data: [],
      filter: 'savings',
    });
  });

  it('should handle SAVINGS_SUCCESS action', () => {
    expect(
      reducer(undefined, {
        type: types.SAVINGS_SUCCESS,
        savings: [{ month: 1, savings: '100.00' }],
      }),
    ).toEqual({
      data: [{ month: 1, savings: '100.00' }],
      filter: 'savings',
    });

    expect(
      reducer(
        {
          data: [{ month: 1, savings: '100.00' }],
        },
        {
          type: types.SAVINGS_SUCCESS,
          savings: [{ month: 2, savings: '200.00' }],
        },
      ),
    ).toEqual({
      data: [{ month: 2, savings: '200.00' }],
    });
  });

  it('should handle SAVINGS_UPDATE_CHART_FILTER action', () => {
    expect(
      reducer(undefined, {
        type: types.SAVINGS_UPDATE_CHART_FILTER,
        filter: 'spend',
      }),
    ).toEqual({
      data: [],
      filter: 'spend',
    });

    expect(
      reducer(
        {
          data: [{ month: 1, savings: '200.00' }],
          filter: 'savings',
        },
        {
          type: types.SAVINGS_UPDATE_CHART_FILTER,
          filter: 'spend',
        },
      ),
    ).toEqual({
      data: [{ month: 1, savings: '200.00' }],
      filter: 'spend',
    });
  });
});

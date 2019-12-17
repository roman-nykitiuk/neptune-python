import * as types from '@/constants/action-types';
import reducer from '@/reducers/marketshare';

describe('marketshare reducer', () => {
  it('should return initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      marketshare: [],
      name: '',
    });
  });

  it('should handle MARKETSHARE_SUCCESS', () => {
    expect(
      reducer(undefined, {
        type: types.MARKETSHARE_SUCCESS,
        marketshare: {
          marketshare: [{ id: 1, name: 'BIO', spend: '100.00' }],
          name: 'Marketshare 2018',
        },
      }),
    ).toEqual({
      marketshare: [{ id: 1, name: 'BIO', spend: '100.00' }],
      name: 'Marketshare 2018',
    });

    expect(
      reducer(
        {
          marketshare: [{ id: 1, name: 'MDT', spend: '200.00' }],
          name: 'Marketshare 2017',
        },
        {
          type: types.MARKETSHARE_SUCCESS,
          marketshare: {
            marketshare: [{ id: 1, name: 'BIO', spend: '100.00' }],
            name: 'Marketshare 2018',
          },
        },
      ),
    ).toEqual({
      marketshare: [{ id: 1, name: 'BIO', spend: '100.00' }],
      name: 'Marketshare 2018',
    });
  });
});

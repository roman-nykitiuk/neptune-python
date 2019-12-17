import * as types from '@/constants/action-types';
import reducer from '@/reducers/dashboard/marketshare';

describe('marketshare reducer', () => {
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
          marketshare: {
            marketshare: [{ id: 1, name: 'MDT', spend: '200.00' }],
            name: 'Marketshare 2017',
          },
          repCases: [
            {
              id: 1,
              product: 'Etrinsia',
              physician: 'Dr. Lusgarten',
            },
          ],
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

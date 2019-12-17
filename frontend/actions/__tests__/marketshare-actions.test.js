import getMarketShare from '@/actions/marketshare-actions';

describe('getMarketShare', () => {
  const mock = getMockAxios();
  const store = getMockStore();

  beforeEach(() => {
    store.clearActions();
  });

  afterEach(() => {
    mock.reset();
  });

  describe('marketshare success', () => {
    const marketshare = {
      name: '2018 Year to Date',
      marketshare: [
        {
          id: 1,
          name: 'MDT',
          units: 10,
          spend: '1000.00',
        },
        {
          id: 2,
          name: 'BIO',
          units: 20,
          spend: '700.50',
        },
      ],
    };

    beforeEach(() => {
      mock.onGet('/api/admin/clients/8/marketshare').reply(200, marketshare);
    });

    it('should dispatch MARKETSHARE_SUCCESS', () => {
      store.dispatch(getMarketShare(8)).then(() => {
        expect(store.getActions()).toEqual([
          {
            type: 'MARKETSHARE_SUCCESS',
            marketshare,
          },
        ]);
      });
    });
  });
});

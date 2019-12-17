import getRepCases from '@/actions/rep-case-actions';
import * as types from '@/constants/action-types';

describe('getMarketShare', () => {
  const mock = getMockAxios();
  const store = getMockStore();

  beforeEach(() => {
    store.clearActions();
  });

  afterEach(() => {
    mock.reset();
  });

  describe('rep cases success', () => {
    const repCases = [
      {
        category: 'VVI Pacemakers',
        id: 36237,
        identifier: '31232123.0-0013CD',
        manufacturer: 'Biotronik',
        model_number: '394936',
      },
    ];
    beforeEach(() => {
      mock.onGet('/api/admin/clients/8/cases').reply(200, repCases);
    });

    it('should dispatch REP_CASE_SUCCESS', () =>
      store.dispatch(getRepCases(8)).then(() => {
        expect(store.getActions()).toEqual([
          {
            type: types.REP_CASE_SUCCESS,
            repCases,
          },
        ]);
      }));
  });
});

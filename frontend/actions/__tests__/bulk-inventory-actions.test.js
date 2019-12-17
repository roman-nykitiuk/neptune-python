import * as types from '@/constants/action-types';
import getBulkInventory from '../bulk-inventory-actions';

describe('getBulkInventory', () => {
  const mock = getMockAxios();
  const store = getMockStore();

  beforeEach(() => {
    store.clearActions();
  });

  afterEach(() => {
    mock.reset();
  });

  describe('bulk inventory success', () => {
    const bulkInventory = { expiring60: 5, expiring30: 10, expired: 2 };
    beforeEach(() => {
      mock.onGet('/api/admin/clients/8/bulk').reply(200, bulkInventory);
    });

    it('should dispatch REP_CASE_SUCCESS', () =>
      store.dispatch(getBulkInventory(8)).then(() => {
        expect(store.getActions()).toEqual([
          {
            type: types.BULK_INVENTORY_SUCCESS,
            bulkInventory,
          },
        ]);
      }));
  });
});

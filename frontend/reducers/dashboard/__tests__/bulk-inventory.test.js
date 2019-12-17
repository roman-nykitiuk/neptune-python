import * as types from '@/constants/action-types';
import reducer from '../bulk-inventory';

describe('bulk inventory reducer', () => {
  it('should return initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      expiring60: 0,
      expiring30: 0,
      expired: 0,
    });
  });

  it('should handle SAVINGS_SUCCESS action', () => {
    expect(
      reducer(undefined, {
        type: types.BULK_INVENTORY_SUCCESS,
        bulkInventory: { expiring60: 10, expiring30: 5, expired: 2 },
      }),
    ).toEqual({ expiring60: 10, expiring30: 5, expired: 2 });

    expect(
      reducer(
        { expiring60: 10, expiring30: 5, expired: 2 },
        {
          type: types.BULK_INVENTORY_SUCCESS,
          bulkInventory: {
            expiring60: 5,
            expiring30: 7,
            expired: 5,
          },
        },
      ),
    ).toEqual({ expiring60: 5, expiring30: 7, expired: 5 });
  });
});

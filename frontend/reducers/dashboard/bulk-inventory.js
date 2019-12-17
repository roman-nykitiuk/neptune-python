import * as types from '@/constants/action-types';

const initialState = {
  expiring60: 0,
  expiring30: 0,
  expired: 0,
};

const bulkInventory = (state = initialState, action) => {
  switch (action.type) {
    case types.BULK_INVENTORY_SUCCESS:
      return { ...state, ...action.bulkInventory };
    default:
      return state;
  }
};

export default bulkInventory;

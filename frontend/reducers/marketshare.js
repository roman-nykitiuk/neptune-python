import * as types from '@/constants/action-types';

const initialState = {
  marketshare: [],
  name: '',
};

const marketshare = (state = initialState, action) => {
  switch (action.type) {
    case types.MARKETSHARE_SUCCESS:
      return { ...action.marketshare };
    default:
      return state;
  }
};

export default marketshare;

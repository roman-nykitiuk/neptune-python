import * as types from '@/constants/action-types';

const repCases = (state = [], action) => {
  switch (action.type) {
    case types.REP_CASE_SUCCESS:
      return action.repCases;
    default:
      return state;
  }
};

export default repCases;

import * as types from '@/constants/action-types';

const initialState = {
  data: [],
  filter: 'savings',
};

const savings = (state = initialState, action) => {
  switch (action.type) {
    case types.SAVINGS_SUCCESS:
      return {
        ...state,
        data: [...action.savings],
      };
    case types.SAVINGS_UPDATE_CHART_FILTER:
      return {
        ...state,
        filter: action.filter,
      };
    default:
      return state;
  }
};

export default savings;

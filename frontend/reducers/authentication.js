import * as types from '@/constants/action-types';
import { saveState, removeState } from '@/local-storage';

const initialState = {
  requesting: false,
  error: null,
  user: null,
  token: null,
};
const authentication = (state = initialState, action) => {
  switch (action.type) {
    case types.LOGIN_REQUEST:
      return {
        ...state,
        requesting: true,
      };
    case types.LOGIN_SUCCESS: {
      const newState = {
        ...state,
        requesting: false,
        user: action.user,
        token: action.token,
        error: null,
      };
      saveState('authentication', newState);
      return newState;
    }
    case types.LOGIN_ERROR:
      return {
        ...state,
        requesting: false,
        error: action.error,
      };
    case types.LOGOUT_COMPLETED:
      removeState('authentication');
      return initialState;
    default:
      return state;
  }
};

export default authentication;

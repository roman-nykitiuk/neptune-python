import * as types from '@/constants/action-types';
import axios from 'axios';

const loginRequest = () => ({
  type: types.LOGIN_REQUEST,
});

const loginSuccess = (user, token) => ({
  type: types.LOGIN_SUCCESS,
  user,
  token,
});

const loginError = error => ({
  type: types.LOGIN_ERROR,
  error,
});

const login = (email, password) => dispatch => {
  dispatch(loginRequest());
  return axios.post('/api/admin/login', { email, password }).then(
    response => {
      const { user, token } = response.data;
      return dispatch(loginSuccess(user, token));
    },
    error => dispatch(loginError(error.response.data.detail)),
  );
};

export default login;

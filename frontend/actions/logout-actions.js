import * as types from '@/constants/action-types';
import sendAdminRequest from '@/utils';

const logoutCompleted = () => ({
  type: types.LOGOUT_COMPLETED,
});

const logout = () => (dispatch, getState) =>
  sendAdminRequest(getState, {
    method: 'post',
    url: '/api/logout',
  }).then(() => dispatch(logoutCompleted()), () => dispatch(logoutCompleted()));

export default logout;

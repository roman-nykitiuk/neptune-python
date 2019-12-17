import { combineReducers } from 'redux';
import authentication from './authentication';
import dashboard from './dashboard/dashboard';

export default combineReducers({
  authentication,
  dashboard,
});

export const getClientId = state => state.authentication.user.admin_client && state.authentication.user.admin_client.id;

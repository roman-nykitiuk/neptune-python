import * as types from '@/constants/action-types';
import sendAdminRequest from '@/utils';

const marketshareSuccess = marketshare => ({
  type: types.MARKETSHARE_SUCCESS,
  marketshare,
});

const getMarketShare = clientId => (dispatch, getState) =>
  sendAdminRequest(getState, {
    method: 'get',
    url: `/api/admin/clients/${clientId}/marketshare`,
  }).then(response => dispatch(marketshareSuccess(response.data)));

export default getMarketShare;

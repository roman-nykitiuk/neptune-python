import * as types from '@/constants/action-types';
import sendAdminRequest from '@/utils';

const repCaseSuccess = repCases => ({
  type: types.REP_CASE_SUCCESS,
  repCases,
});

const getRepCases = clientId => (dispatch, getState) =>
  sendAdminRequest(getState, {
    method: 'get',
    url: `/api/admin/clients/${clientId}/cases`,
  }).then(response => dispatch(repCaseSuccess(response.data)));

export default getRepCases;

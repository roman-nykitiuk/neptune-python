import * as types from '@/constants/action-types';
import sendAdminRequest from '@/utils';

const savingsSuccess = savings => ({
  type: types.SAVINGS_SUCCESS,
  savings,
});

const getSavings = clientId => (dispatch, getState) =>
  sendAdminRequest(getState, {
    method: 'get',
    url: `api/admin/clients/${clientId}/savings`,
  }).then(response => dispatch(savingsSuccess(response.data)));

export function updateChartFilter(filter) {
  return {
    type: types.SAVINGS_UPDATE_CHART_FILTER,
    filter,
  };
}

export default getSavings;

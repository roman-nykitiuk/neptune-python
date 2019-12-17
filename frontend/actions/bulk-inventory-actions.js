import * as types from '@/constants/action-types';
import sendAdminRequest from '@/utils';

const bulkInventorySuccess = bulkInventory => ({
  type: types.BULK_INVENTORY_SUCCESS,
  bulkInventory,
});

const getBulkInventory = clientId => (dispatch, getState) =>
  sendAdminRequest(getState, {
    method: 'get',
    url: `api/admin/clients/${clientId}/bulk`,
  }).then(response => dispatch(bulkInventorySuccess(response.data)));

export default getBulkInventory;

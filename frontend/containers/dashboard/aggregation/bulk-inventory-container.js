import { connect } from 'react-redux';
import getBulkInventory from '@/actions/bulk-inventory-actions';
import { getClientId } from '@/reducers/index';
import BulkInventory from '@/components/dashboard/aggregation/bulk-inventory';

const mapStateToProps = state => ({
  bulkInventory: state.dashboard.bulkInventory,
  clientId: getClientId(state),
});

const mapDispatchToProps = {
  getBulkInventory,
};

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(BulkInventory);

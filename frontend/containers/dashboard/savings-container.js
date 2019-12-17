import { connect } from 'react-redux';
import getSavings, { updateChartFilter } from '@/actions/savings-actions';
import Savings from '@/components/dashboard/savings/savings';

const mapStateToProps = state => ({
  savings: state.dashboard.savings,
});

const mapDispatchToProps = {
  getSavings,
  updateChartFilter,
};

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(Savings);

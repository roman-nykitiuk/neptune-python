import { connect } from 'react-redux';
import RepCase from '@/components/dashboard/rep-case';
import getRepCases from '@/actions/rep-case-actions';

const mapStateToProps = state => ({
  repCases: state.dashboard.repCases,
});

const mapDispatchToProps = {
  getRepCases,
};

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(RepCase);

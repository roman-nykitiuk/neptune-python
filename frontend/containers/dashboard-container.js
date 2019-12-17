import { connect } from 'react-redux';
import Dashboard from '@/components/dashboard/dashboard';
import { getClientId } from '@/reducers/index';

const mapStateToProps = state => ({
  clientId: getClientId(state),
});

export default connect(mapStateToProps)(Dashboard);

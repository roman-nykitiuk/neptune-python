import { connect } from 'react-redux';
import Users from '@/components/users/users';
import { getClientId } from '@/reducers/index';

const mapStateToProps = state => ({
  clientId: getClientId(state),
});

export default connect(mapStateToProps)(Users);

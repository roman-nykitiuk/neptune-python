import { connect } from 'react-redux';
import AdminPage from '@/components/pages/admin-page';

const mapStateToProps = state => ({
  isAuthenticated: !!state.authentication.token,
  user: state.authentication.user,
});

export default connect(mapStateToProps)(AdminPage);

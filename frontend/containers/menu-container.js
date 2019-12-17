import { connect } from 'react-redux';
import Menu from '@/components/menu';
import logout from '@/actions/logout-actions';

const mapDispatchToProps = {
  logout,
};

export default connect(
  null,
  mapDispatchToProps,
)(Menu);

import { connect } from 'react-redux';
import LoginForm from '@/components/login-form';
import login from '@/actions/login-actions';

const mapStateToProps = state => ({
  authentication: state.authentication,
});

const mapDispatchToProps = {
  login,
};

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(LoginForm);

import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Redirect } from 'react-router-dom';
import { FormWrapper, Input, SubmitButton, FormGroup, ErrorMessage } from './login-form-styles';

export default class LoginForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      email: '',
      password: '',
    };
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleSubmit(event) {
    const { email, password } = this.state;
    event.preventDefault();
    this.props.login(email, password);
  }

  handleInputChange(event) {
    const { name } = event.target;
    this.setState({
      [name]: event.target.value,
    });
  }

  render() {
    const { email, password } = this.state;
    const { error, requesting, token } = this.props.authentication;
    if (token) {
      return <Redirect to="/admin" />;
    }
    return (
      <FormWrapper>
        <h2>Login</h2>
        {error && <ErrorMessage>{error}</ErrorMessage>}
        <form onSubmit={this.handleSubmit}>
          <FormGroup>
            <Input
              id="email"
              type="email"
              name="email"
              value={email}
              onChange={this.handleInputChange}
              placeholder="Email address"
            />
          </FormGroup>
          <FormGroup>
            <Input
              id="password"
              type="password"
              name="password"
              value={password}
              onChange={this.handleInputChange}
              placeholder="Password"
            />
          </FormGroup>
          <SubmitButton type="submit" value="LOG IN" disabled={requesting} />
        </form>
      </FormWrapper>
    );
  }
}

LoginForm.propTypes = {
  login: PropTypes.func.isRequired,
  authentication: PropTypes.shape({
    requesting: PropTypes.bool.isRequired,
    error: PropTypes.string,
    token: PropTypes.string,
    user: PropTypes.object,
  }).isRequired,
};

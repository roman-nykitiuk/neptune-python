import React, { Component } from 'react';
import { Redirect } from 'react-router-dom';
import PropTypes from 'prop-types';
import LeftMenuContainer from '@/containers/menu-container';
import Header from '@/components/header';
import { Body } from '@/components/pages/admin-styles';

export default class AdminPage extends Component {
  render() {
    const { isAuthenticated, user, children } = this.props;
    if (!isAuthenticated) {
      return <Redirect to="/admin/login" />;
    }
    return (
      <div>
        <Header user={user} />
        <LeftMenuContainer />
        <Body>{children}</Body>
      </div>
    );
  }
}

AdminPage.defaultProps = {
  user: {},
};

AdminPage.propTypes = {
  children: PropTypes.element.isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
  user: PropTypes.shape({
    name: PropTypes.string,
  }),
};

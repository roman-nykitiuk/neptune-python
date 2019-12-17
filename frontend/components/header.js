import React from 'react';
import PropTypes from 'prop-types';
import { Navbar, Branding, UserNav, UserInfo, UserIcon } from '@/components/header-styles';

const Header = props => {
  const { user } = props;
  return (
    <Navbar>
      <Branding>
        <img src="/static/images/logo.png" alt="logo" />
      </Branding>
      <UserNav>
        <UserInfo>
          <span>{user.name}</span>
          <UserIcon src="/static/images/icons/user.svg" alt="user" />
        </UserInfo>
      </UserNav>
    </Navbar>
  );
};

Header.propTypes = {
  user: PropTypes.shape({
    name: PropTypes.string.isRequired,
  }).isRequired,
};

export default Header;

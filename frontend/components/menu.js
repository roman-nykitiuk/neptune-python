import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { MenuWrapper, MenuItem } from './menu-styles';

export default class Menu extends Component {
  constructor(props) {
    super(props);
    this.onLogoutClick = this.onLogoutClick.bind(this);
  }

  onLogoutClick(e) {
    e.preventDefault();
    this.props.logout();
  }

  render() {
    const menuItems = [
      { to: '/admin', alt: 'home', icon: 'home.svg', title: 'Home' },
      { to: '/admin', alt: 'device', icon: 'device.svg', title: 'Devices' },
      { to: '/admin/users', alt: 'users', icon: 'group.svg', title: 'Users' },
      { to: '/admin', alt: 'calendar', icon: 'calendar.svg', title: 'Calendar' },
      { to: '/admin', alt: 'repcase', icon: 'repcase.svg', title: 'Repcase' },
      { to: '/admin', alt: 'analytic', icon: 'analytic.svg', title: 'Analytics' },
      { to: '/admin', alt: 'logout', icon: 'logout.png', title: 'Logout', onClick: this.onLogoutClick },
    ];

    return (
      <MenuWrapper>
        {menuItems.map(item => (
          <MenuItem to={item.to} key={item.alt} onClick={item.onClick}>
            <img src={`/static/images/icons/${item.icon}`} alt={item.alt} />
            <span>{item.title}</span>
          </MenuItem>
        ))}
      </MenuWrapper>
    );
  }
}

Menu.propTypes = {
  logout: PropTypes.func.isRequired,
};

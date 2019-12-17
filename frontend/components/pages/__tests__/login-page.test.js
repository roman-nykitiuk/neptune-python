import React from 'react';
import LoginPage from '@/components/pages/login-page';
import LoginFormContainer from '@/containers/login-form-container';

describe('LoginPage', () => {
  it('should render LoginFormContainer', () => {
    const wrapper = shallow(<LoginPage />);
    expect(wrapper.find(LoginFormContainer).length).toEqual(1);
  });
});

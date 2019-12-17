import React from 'react';
import LoginFormContainer from '@/containers/login-form-container';
import { Wrapper, LeftPanel, RightPanel } from './login-page-styles';

const LoginPage = () => (
  <Wrapper>
    <LeftPanel>
      <img src="/static/images/logo.png" alt="logo" />
      <p>Just what the doctor ordered.</p>
      <p>Data-driven medical device purchasing.</p>
    </LeftPanel>
    <RightPanel>
      <LoginFormContainer />
    </RightPanel>
  </Wrapper>
);

export default LoginPage;

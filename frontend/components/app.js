import React from 'react';
import { BrowserRouter, Route, Switch } from 'react-router-dom';
import Loadable from 'react-loadable';

const Loading = () => null;

const HomePage = Loadable({
  loader: () => import('./pages/home-page'),
  loading: Loading,
});

const LoginPage = Loadable({
  loader: () => import('./pages/login-page'),
  loading: Loading,
});

const UsersPage = Loadable({
  loader: () => import('./pages/users-page'),
  loading: Loading,
});

const App = () => {
  let routesProps = {};
  if (process.env.NODE_ENV === 'development') {
    routesProps = { key: Math.random() };
  }

  return (
    <BrowserRouter>
      <div>
        <Switch {...routesProps}>
          <Route exact path="/admin/" component={HomePage} />
          <Route path="/admin/login" component={LoginPage} />
          <Route path="/admin/users" component={UsersPage} />
        </Switch>
      </div>
    </BrowserRouter>
  );
};

export default App;

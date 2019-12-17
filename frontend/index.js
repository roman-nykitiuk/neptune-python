/* eslint-disable import/no-extraneous-dependencies, global-require */
import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { AppContainer } from 'react-hot-loader';
import App from './components/app';
import configureStore from './configure-store';
import { loadState } from './local-storage';
import './global-styles.css';

const store = configureStore({ authentication: loadState('authentication') });

const render = Component => {
  ReactDOM.render(
    <AppContainer>
      <Provider store={store}>
        <Component />
      </Provider>
    </AppContainer>,
    document.getElementById('frontend'),
  );
};

render(App);

/* istanbul ignore if */
if (module.hot) {
  module.hot.accept('./components/app', () => {
    const NextApp = require('./components/app').default;
    render(NextApp);
  });
}

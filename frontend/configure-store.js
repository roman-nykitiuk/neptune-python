import { createStore, applyMiddleware, compose } from 'redux';
import thunkMiddleware from 'redux-thunk';
import rootReducer from '@/reducers';

const configureStore = initialState => {
  const middlewares = [thunkMiddleware];

  /* istanbul ignore if */
  if (process.env.NODE_ENV === 'development') {
    /* eslint-disable global-require,import/no-extraneous-dependencies */
    const { logger } = require('redux-logger');
    middlewares.push(logger);
  }
  /* eslint-disable no-underscore-dangle */
  const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;
  /* eslint-enable */
  return createStore(rootReducer, initialState, composeEnhancers(applyMiddleware(...middlewares)));
};

export default configureStore;

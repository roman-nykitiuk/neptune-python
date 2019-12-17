/* istanbul ignore file */

import Enzyme, { shallow, render, mount } from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import configureStore from 'redux-mock-store';
import thunkMiddleware from 'redux-thunk';

// Setup enzyme's react adapter
Enzyme.configure({ adapter: new Adapter() });

// Make Enzyme functions available in all test files without importing
global.shallow = shallow;
global.render = render;
global.mount = mount;

/* This is a little hack to wait for promises to resolve before executing
 * the assertions
 *
 * Usage:
 *  await flushAllPromises();
 *  wrapper.update(); // Maybe you need to update the enzyme wrapper first
 *  // execute asertions for async actions
 */
global.flushAllPromises = () => new Promise(r => setTimeout(r));
global.getMockAxios = () => new MockAdapter(axios);
global.getMockStore = (initialState = { authentication: { token: 'token' } }) => {
  const middlewares = [thunkMiddleware];
  const mockStore = configureStore(middlewares);
  return mockStore(initialState);
};

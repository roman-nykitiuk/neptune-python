import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import configureStore from 'redux-mock-store';
import thunkMiddleware from 'redux-thunk';
import login from '@/actions/login-actions';

describe('async login', () => {
  const mock = new MockAdapter(axios);
  const middlewares = [thunkMiddleware];
  const mockStore = configureStore(middlewares);
  const store = mockStore();

  beforeEach(() => {
    store.clearActions();
  });

  afterEach(() => {
    mock.reset();
  });

  describe('request success', () => {
    beforeEach(() => {
      mock.onPost('/api/admin/login').reply(200, { user: 'test@email.com', token: 'authenticated-token' });
    });

    it('should dispatch LOGIN_REQUEST and LOGIN_SUCCESS actions', () => {
      store.dispatch(login('test@email.com', 'password')).then(() => {
        expect(store.getActions()).toEqual([
          { type: 'LOGIN_REQUEST' },
          {
            type: 'LOGIN_SUCCESS',
            user: 'test@email.com',
            token: 'authenticated-token',
          },
        ]);
      });
    });
  });

  describe('request error', () => {
    beforeEach(() => {
      mock.onPost('/api/admin/login').reply(400, { detail: 'Error message' });
    });

    it('should dispatch LOGIN_REQUEST and LOGIN_ERROR actions', () =>
      store.dispatch(login('test@email.com', 'password')).then(() => {
        expect(store.getActions()).toEqual([
          { type: 'LOGIN_REQUEST' },
          {
            type: 'LOGIN_ERROR',
            error: 'Error message',
          },
        ]);
      }));
  });
});

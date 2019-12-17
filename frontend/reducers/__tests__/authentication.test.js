import * as types from '@/constants/action-types';
import reducer from '@/reducers/authentication';
import { saveState, removeState } from '@/local-storage';

jest.mock('@/local-storage', () => ({
  saveState: jest.fn(),
  removeState: jest.fn(),
}));

describe('authentication reducer', () => {
  beforeEach(() => {
    saveState.mockClear();
    removeState.mockClear();
  });

  it('should return initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      requesting: false,
      error: null,
      user: null,
      token: null,
    });
  });

  it('should handle LOGIN_REQUEST', () => {
    expect(reducer(undefined, { type: types.LOGIN_REQUEST })).toEqual({
      requesting: true,
      error: null,
      user: null,
      token: null,
    });
    expect(
      reducer(
        {
          requesting: false,
          error: 'Invalid user',
          user: null,
          token: null,
        },
        { type: types.LOGIN_REQUEST },
      ),
    ).toEqual({
      requesting: true,
      error: 'Invalid user',
      user: null,
      token: null,
    });
  });

  it('should handle LOGIN_SUCCESS', () => {
    expect(
      reducer(undefined, {
        type: types.LOGIN_SUCCESS,
        user: { username: 'admin' },
        token: 'token',
      }),
    ).toEqual({
      requesting: false,
      error: null,
      user: { username: 'admin' },
      token: 'token',
    });

    expect(
      reducer(
        {
          requesting: true,
          error: 'Invalid',
          user: null,
          token: null,
        },
        {
          type: types.LOGIN_SUCCESS,
          user: { username: 'admin' },
          token: 'token',
        },
      ),
    ).toEqual({
      requesting: false,
      error: null,
      user: { username: 'admin' },
      token: 'token',
    });
  });

  it('should handle LOGIN_ERROR', () => {
    expect(
      reducer(undefined, {
        type: types.LOGIN_ERROR,
        error: 'Invalid user',
      }),
    ).toEqual({
      requesting: false,
      error: 'Invalid user',
      user: null,
      token: null,
    });

    expect(
      reducer(
        {
          requesting: true,
          error: null,
          user: null,
          token: null,
        },
        {
          type: types.LOGIN_ERROR,
          error: 'Invalid',
        },
      ),
    ).toEqual({
      requesting: false,
      error: 'Invalid',
      user: null,
      token: null,
    });
  });

  it('should call saveState when handle LOGIN_SUCCESS', () => {
    reducer(undefined, {
      type: types.LOGIN_SUCCESS,
      user: { username: 'admin' },
      token: 'token',
    });
    expect(saveState).toHaveBeenCalledWith('authentication', {
      requesting: false,
      user: { username: 'admin' },
      token: 'token',
      error: null,
    });
  });

  it('should call removeState when handle LOGOUT_COMPLETED', () => {
    expect(
      reducer(undefined, {
        type: types.LOGOUT_COMPLETED,
      }),
    ).toEqual({
      requesting: false,
      error: null,
      user: null,
      token: null,
    });
    expect(removeState).toHaveBeenCalledWith('authentication');
  });
});

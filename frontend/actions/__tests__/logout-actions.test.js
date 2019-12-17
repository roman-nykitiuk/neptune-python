import logout from '@/actions/logout-actions';

describe('async logout', () => {
  const mock = getMockAxios();
  const store = getMockStore();

  beforeEach(() => {
    store.clearActions();
  });

  afterEach(() => {
    mock.reset();
  });

  describe('request logout api success', () => {
    beforeEach(() => {
      mock.onPost('/api/logout').reply(200);
    });

    it('should dispatch LOGOUT_COMPLETED actions', () => {
      store.dispatch(logout()).then(() => {
        expect(store.getActions()).toEqual([{ type: 'LOGOUT_COMPLETED' }]);
      });
    });
  });

  describe('request logout api error', () => {
    beforeEach(() => {
      mock.onPost('/api/logout').reply(400);
    });

    it('should dispatch LOGOUT_COMPLETED actions', () => {
      store.dispatch(logout()).then(() => {
        expect(store.getActions()).toEqual([{ type: 'LOGOUT_COMPLETED' }]);
      });
    });
  });
});

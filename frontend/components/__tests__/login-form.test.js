import React from 'react';
import LoginForm from '@/components/login-form';
import { ErrorMessage } from '@/components/login-form-styles';

describe('LoginForm', () => {
  const mockLogin = jest.fn();
  let wrapper;
  let authentication;

  describe('Authentication token is missing', () => {
    beforeEach(() => {
      authentication = {
        token: '',
        requesting: false,
        error: 'Invalid email address',
      };
      wrapper = shallow(<LoginForm login={mockLogin} authentication={authentication} />);
    });

    describe('render()', () => {
      it('should render the component', () => {
        expect(wrapper.find('h2').text()).toEqual('Login');
      });

      describe('error presents', () => {
        it('should render error message', () => {
          expect(wrapper.find('h2').text()).toEqual('Login');
          expect(wrapper.find(ErrorMessage).length).toEqual(1);
          expect(
            wrapper
              .find(ErrorMessage)
              .children()
              .text(),
          ).toContain('Invalid email address');
        });
      });
    });

    describe('handleSubmit()', () => {
      it('should call login', () => {
        const email = 'test@email.com';
        const password = 'my-secure-password';
        wrapper.find('#email').simulate('change', { target: { name: 'email', value: email } });
        wrapper.find('#password').simulate('change', { target: { name: 'password', value: password } });
        wrapper.find('form').simulate('submit', { preventDefault() {} });
        expect(mockLogin.mock.calls.length).toBe(1);
        expect(mockLogin.mock.calls[0][0]).toEqual(email);
        expect(mockLogin.mock.calls[0][1]).toEqual(password);
      });
    });
  });

  describe('Token is present', () => {
    beforeEach(() => {
      authentication = { requesting: false, token: 'token' };
      wrapper = shallow(<LoginForm login={mockLogin} authentication={authentication} />);
    });

    it('should redirect to dashboard', () => {
      expect(wrapper.find('Redirect').length).toEqual(1);
    });
  });
});

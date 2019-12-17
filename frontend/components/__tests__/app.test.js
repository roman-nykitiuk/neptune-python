import React from 'react';
import App from '@/components/app';

jest.mock('react-plotly.js', () => () => null);

describe('App', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = shallow(<App />);
  });

  it('should render BrowserRouter', () => {
    expect(wrapper.find('BrowserRouter').length).toEqual(1);
  });

  it('should render Route', () => {
    expect(wrapper.find('Route').length).toEqual(2);
  });
});

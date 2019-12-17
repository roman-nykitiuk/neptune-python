import axios from 'axios';

const sendAdminRequest = (getState, options) => {
  const { token } = getState().authentication;

  return axios({
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Token ${token}`,
    },
  });
};

export const colorOf = percent => {
  const ranges = [
    { min: 0, max: 10, color: '#79aeeb' },
    { min: 11, max: 20, color: '#8eb2dd' },
    { min: 21, max: 30, color: '#6784a6' },
    { min: 31, max: 100, color: '#496b92' },
  ];
  const match = ranges.find(r => percent >= r.min && percent <= r.max);
  return match ? match.color : '#8eb2dd';
};

export const getLongMonth = intMonth => {
  const monthNames = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ];
  return monthNames[intMonth];
};

export const capitalizeFirstLetter = str => str.charAt(0).toUpperCase() + str.slice(1);

export default sendAdminRequest;

import reducer from '@/reducers/dashboard/dashboard';

it('should return initial state', () => {
  expect(reducer(undefined, {})).toEqual({
    marketshare: {
      marketshare: [],
      name: '',
    },
    repCases: [],
    savings: {
      data: [],
      filter: 'savings',
    },
    bulkInventory: {
      expiring60: 0,
      expiring30: 0,
      expired: 0,
    },
  });
});

import React from 'react';
import Table from '@/components/common/table';
import StyledTable from '@/components/common/table-styles';

describe('Table', () => {
  let wrapper;
  let props;

  beforeEach(() => {
    props = {
      titles: { column1: 'Column1', column2: 'Column2' },
      rows: [
        { id: 1, column1: '1', column2: '2' },
        { id: 2, column1: '3', column2: '4' },
        { id: 3, column1: '5', column2: '6' },
      ],
    };
    wrapper = shallow(<Table {...props} />);
  });

  it('should render a table', () => {
    expect(wrapper.find(StyledTable).length).toEqual(1);
  });

  it('should render table headers', () => {
    const ths = wrapper.find('th');
    expect(ths.length).toEqual(2);
    expect(ths.at(0).text()).toEqual('Column1');
    expect(ths.at(1).text()).toEqual('Column2');
  });

  it('should render table rows', () => {
    const trs = wrapper.find('tbody > tr');
    expect(trs.length).toEqual(3);
    expect(trs.at(0).text()).toEqual('12');
    expect(trs.at(1).text()).toEqual('34');
    expect(trs.at(2).text()).toEqual('56');
  });
});

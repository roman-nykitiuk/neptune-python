import React from 'react';
import PropTypes from 'prop-types';
import StyledTable from './table-styles';

const Table = ({ className, titles, rows }) => {
  const keys = Object.keys(titles);
  return (
    <StyledTable className={className}>
      <thead>
        <tr>{keys.map(key => <th key={key}>{titles[key]}</th>)}</tr>
      </thead>
      <tbody>{rows.map(row => <tr key={row.id}>{keys.map(key => <td key={key}>{row[key]}</td>)}</tr>)}</tbody>
    </StyledTable>
  );
};

Table.defaultProps = {
  className: '',
};

Table.propTypes = {
  className: PropTypes.string,
  titles: PropTypes.objectOf(PropTypes.string).isRequired,
  rows: PropTypes.arrayOf(PropTypes.object).isRequired,
};

export default Table;

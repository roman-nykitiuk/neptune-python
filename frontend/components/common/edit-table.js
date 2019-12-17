import React from 'react';
import PropTypes from 'prop-types';
import StyledEditTable from './edit-table-styles';

const EditTable = ({ className, titles, rows }) => {
  const keys = Object.keys(titles);
  return (
    <StyledEditTable className={className}>
      <thead>
        <tr>
          <td colSpan="7">
            <h2>Users</h2>
            <div className="download">Download</div>
            <div className="filter">
              <input type="text" placeholder="User search..." />
              <select>
                <option value="0">in All</option>
              </select>
            </div>
            <div className="more">...</div>
            <div className="add">Add User</div>
          </td>
        </tr>
        <tr>{keys.map(key => <th key={key}>{titles[key]}</th>)}</tr>
      </thead>
      <tbody>
        {rows.map(row => <tr key={row.id}>{keys.map(key => <td key={key}>{row[key]}</td>)}</tr>)}
        <tr>
          <td colSpan="7">
            <div className="more">Load More...</div>
          </td>
        </tr>
      </tbody>
    </StyledEditTable>
  );
};

EditTable.defaultProps = {
  className: '',
};

EditTable.propTypes = {
  className: PropTypes.string,
  titles: PropTypes.objectOf(PropTypes.string).isRequired,
  rows: PropTypes.arrayOf(PropTypes.object).isRequired,
};

export default EditTable;

import styled from 'styled-components';

const StyledTable = styled.table`
  border-collapse: collapse;
  color: #a3a6b4;
  font-size: 11px;
  text-align: left;

  > thead {
    display: table;
    table-layout: fixed;
    width: 100%;

    th {
      background: #f5f6fa;
      padding: 15px 10px;
      text-transform: uppercase;
      white-space: nowrap;
    }
  }
  > tbody {
    display: block;
    max-height: 400px;
    overflow: auto;

    tr {
      display: table;
      table-layout: fixed;
      width: 100%;

      td {
        padding: 10px;
        border-bottom: solid 1px #f1f1f3;
        font-size: 13px;
        font-weight: 300;
      }
    }
  }
`;

export default StyledTable;

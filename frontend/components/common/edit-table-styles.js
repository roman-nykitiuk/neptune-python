import styled from 'styled-components';

const StyledEditTable = styled.table`
  border-collapse: collapse;
  color: #666;
  font-size: 11px;
  text-align: left;
  font-family: Avenir;
  background: #fff;

  > thead {
    display: table;
    table-layout: fixed;
    width: 100%;

    th {
      background: #fff;
      padding: 15px 10px;
      white-space: nowrap;
      border-bottom: 1px solid black;
      color: black;
      font-size: 16px;
      font-weight: 400;
    }

    td {
      padding: 10px;
      h2 {
        display: block;
        float: left;
        font-size: 14px;
        color: #004799;
        text-transform: uppercase;
      }
      ,
      div {
        float: right;
      }
      div.more {
        line-height: 3;
        padding: 0 15px;
        margin: 0 10px;
        background: #d0d0d0;
        opacity: 0.2;
        &:hover {
          opacity: 0.8;
        }
      }
      div.add {
        background: #d0d0d0;
        opacity: 0.2;
        padding: 0 20px;
        line-height: 3;
        font-weight: 400;
        cursor: pointer;

        &:hover {
          opacity: 0.8;
        }
      }
      div.filter {
        input {
          line-height: 3;
          width: 136px;
        }
      }
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
        border-bottom: 1px solid #979797;

        div.more {
          margin: 0 auto;
          font-size: 14px;
          color: #0a488f;
          text-align: center;
          background: #d0d0d0;
          font-weight: 600;
          padding: 0;
          width: 35%;
          line-height: 3.5;
          width: 35%;
        }
      }
    }
  }
`;

export default StyledEditTable;

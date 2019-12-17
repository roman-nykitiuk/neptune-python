import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { Title } from '../dashboard-styles';
import { SubWrapper } from './aggregation-styles';

const Content = styled.div`
  display: flex;
  margin-top: 14px;

  > div {
    flex: 0 0 33.33%;
    display: flex;
    align-items: center;
    flex-direction: column;
    font-size: 13px;
    color: #666666;

    img {
      width: 43px;
    }
  }
`;

export default class BulkInventory extends React.Component {
  componentDidMount() {
    const { getBulkInventory, clientId } = this.props;
    getBulkInventory(clientId);
  }
  render() {
    const { expiring60, expiring30, expired } = this.props.bulkInventory;
    return (
      <SubWrapper>
        <Title>Bulk Inventory</Title>
        <Content>
          <div>
            <img src="/static/images/icons/expiring60.svg" alt="Expiring in 60 days" />
            <p>{expiring60} Items Expiring</p>
          </div>
          <div>
            <img src="/static/images/icons/expiring30.png" alt="Expiring in 30 days" />
            <p>{expiring30} Items Low In Stock</p>
          </div>
          <div>
            <img src="/static/images/icons/expired.svg" alt="Expired" />
            <p>{expired} Items Out Of Stock</p>
          </div>
        </Content>
      </SubWrapper>
    );
  }
}

BulkInventory.propTypes = {
  bulkInventory: PropTypes.shape({
    expiring60: PropTypes.number.isRequired,
    expiring30: PropTypes.number.isRequired,
    expired: PropTypes.number.isRequired,
  }).isRequired,
  getBulkInventory: PropTypes.func.isRequired,
  clientId: PropTypes.number.isRequired,
};

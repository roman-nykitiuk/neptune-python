import React, { Component } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import MarketshareChart from './marketshare-chart';
import MarketShareTable from './marketshare-table';
import { Section, Title } from './dashboard-styles';

const MarketshareWrapper = styled(Section)`
  overflow: hidden;
  flex: 1 1 600px;
  margin-right: 20px;
`;

const Content = styled.div`
  display: flex;
`;

export default class MarketShare extends Component {
  componentDidMount() {
    const { getMarketShare, clientId } = this.props;
    getMarketShare(clientId);
  }

  render() {
    const { marketshare, name } = this.props.marketshare;
    return (
      <MarketshareWrapper>
        <Title>{name} Market Share</Title>
        <Content>
          <MarketshareChart marketshare={marketshare} />
          {marketshare.length > 0 ? <MarketShareTable marketshare={marketshare} /> : <p>No data found</p>}
        </Content>
      </MarketshareWrapper>
    );
  }
}

MarketShare.propTypes = {
  getMarketShare: PropTypes.func.isRequired,
  clientId: PropTypes.number.isRequired,
  marketshare: PropTypes.shape({
    marketshare: PropTypes.array,
    name: PropTypes.string,
  }).isRequired,
};

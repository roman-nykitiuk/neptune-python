import React, { Component } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import Table from '@/components/common/table';

export const StyledTable = styled(Table)`
  flex: 1;
  min-width: 300px;
`;

export default class MarketshareTable extends Component {
  render() {
    const { marketshare } = this.props;
    const titles = { name: 'Vendor', units: 'Units', spend: 'Spend', marketshare: 'MS' };
    const sum = marketshare.reduce((acc, ms) => acc + parseFloat(ms.spend), 0);
    const rows = marketshare.map(ms => ({
      ...ms,
      spend: `$${Number(ms.spend).toLocaleString('en-EN')}`,
      marketshare: `${((ms.spend / sum) * 100.0).toFixed(1)}%`,
    }));
    return <StyledTable titles={titles} rows={rows} />;
  }
}

MarketshareTable.propTypes = {
  marketshare: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
      spend: PropTypes.string,
      units: PropTypes.number,
    }),
  ).isRequired,
};

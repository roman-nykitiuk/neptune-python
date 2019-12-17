import React, { Component } from 'react';
import PropTypes from 'prop-types';
import RepCaseContainer from '@/containers/dashboard/rep-case-container';
import MarketShareContainer from '@/containers/dashboard/marketshare-container';
import SavingsContainer from '@/containers/dashboard/savings-container';
import { Wrapper, FirstRow, SecondRow } from './dashboard-styles';
import Aggregation from './aggregation/aggregation';

export default class Dashboard extends Component {
  render() {
    const { clientId } = this.props;
    return (
      <Wrapper>
        <FirstRow>
          <RepCaseContainer clientId={clientId} />
          <Aggregation />
        </FirstRow>
        <SecondRow>
          <MarketShareContainer clientId={clientId} />
          <SavingsContainer clientId={clientId} filters={['savings', 'spend']} />
        </SecondRow>
      </Wrapper>
    );
  }
}

Dashboard.propTypes = {
  clientId: PropTypes.number.isRequired,
};

import React from 'react';
import PropTypes from 'prop-types';
import { Title } from '../dashboard-styles';
import { SubWrapper, Total, DownValue } from './aggregation-styles';

const Spend = ({ total, currentMonth }) => (
  <SubWrapper>
    <Title>Spending Per Category</Title>
    <Total>${total}</Total>
    <DownValue>{currentMonth} this month</DownValue>
  </SubWrapper>
);

Spend.propTypes = {
  total: PropTypes.number.isRequired,
  currentMonth: PropTypes.number.isRequired,
};

export default Spend;

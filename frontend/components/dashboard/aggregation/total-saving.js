import React from 'react';
import PropTypes from 'prop-types';
import { Title } from '../dashboard-styles';
import { SubWrapper, Total, UpValue } from './aggregation-styles';

const TotalSaving = ({ total, currentMonth }) => (
  <SubWrapper>
    <Title>Total Savings</Title>
    <Total>${total}</Total>
    <UpValue>{currentMonth} from last month</UpValue>
  </SubWrapper>
);

TotalSaving.propTypes = {
  total: PropTypes.number.isRequired,
  currentMonth: PropTypes.number.isRequired,
};

export default TotalSaving;

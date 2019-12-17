import React, { Component } from 'react';
import BulkInventoryContainer from '@/containers/dashboard/aggregation/bulk-inventory-container';
import TotalSaving from './total-saving';
import Spend from './spend';
import { Wrapper } from './aggregation-styles';

export default class Aggregation extends Component {
  render() {
    return (
      <Wrapper>
        <TotalSaving total={1000} currentMonth={12} />
        <Spend total={2000} currentMonth={600} />
        <BulkInventoryContainer expiring60={42} expiring30={12} expired={21} />
      </Wrapper>
    );
  }
}

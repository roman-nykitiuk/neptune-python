import React, { Component } from 'react';
import styled from 'styled-components';
import Table from '@/components/common/table';
import { Section, Title } from './dashboard-styles';

const Wrapper = styled(Section)`
  flex: 0 0 calc(66.67% - 20px);
  height: 450px;
  background-color: white;
`;

const RepcaseTable = styled(Table)`
  margin-top: 20px;
  width: 100%;
`;

export default class Repcase extends Component {
  render() {
    const titles = {
      physician: 'Physician',
      manufacture: 'Manufacturer',
      model_number: 'Model no.',
      serial_number: 'Serial No.',
      client: 'Client',
      purchase_type: 'Purchase Type',
    };
    return (
      <Wrapper>
        <Title>Today&apos;s Cases</Title>
        <RepcaseTable titles={titles} rows={[]} />
      </Wrapper>
    );
  }
}

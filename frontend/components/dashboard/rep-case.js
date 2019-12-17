import React, { Component } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import Table from '@/components/common/table';
import { Section, Title } from './dashboard-styles';

const Wrapper = styled(Section)`
  flex: 0 0 calc(66.67% - 20px);
  height: 450px;
  background-color: white;

  > p {
    text-align: center;
  }
`;

export const RepcaseTable = styled(Table)`
  margin-top: 20px;
  width: 100%;
  min-width: 650px;

  tbody {
    max-height: 340px;

    ::-webkit-scrollbar {
      width: 1px;
    }

    ::-webkit-scrollbar-track-piece {
      background-color: #fff;
    }

    ::-webkit-scrollbar-thumb {
      background-color: #ccc;
    }
  }
`;

export default class RepCase extends Component {
  componentDidMount() {
    const { getRepCases, clientId } = this.props;
    getRepCases(clientId);
  }

  render() {
    const { repCases } = this.props;
    const titles = {
      physician: 'Physician',
      manufacturer: 'Manufacturer',
      model_number: 'Model no.',
      identifier: 'Serial No.',
      product: 'Device',
      purchase_type: 'Purchase Type',
    };

    return (
      <Wrapper>
        <Title>Today&apos;s Cases</Title>
        {repCases.length > 0 ? <RepcaseTable titles={titles} rows={repCases} /> : <p>No data found</p>}
      </Wrapper>
    );
  }
}

RepCase.propTypes = {
  getRepCases: PropTypes.func.isRequired,
  clientId: PropTypes.number.isRequired,
  repCases: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      identifier: PropTypes.string.isRequired,
      purchase_type: PropTypes.string.isRequired,
      physician: PropTypes.string.isRequired,
      manufacturer: PropTypes.string.isRequired,
      category: PropTypes.string.isRequired,
      product: PropTypes.string.isRequired,
      model_number: PropTypes.string.isRequired,
    }),
  ).isRequired,
};

import React, { Component } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { getLongMonth } from '@/utils';
import { Section, Title } from '../dashboard-styles';
import SavingsChart from './savings-chart';

const Wrapper = styled(Section)`
  flex: 1 1 600px;
`;

const WrapperHeader = styled.div`
  flex-direction: row;
  display: flex;
`;

export const SavingsTable = styled.table`
  margin-top: 10px;
  font-weight: 400;
  font-size: 11px;
  text-align: left;
  text-transform: uppercase;
  color: #a3a6b4;
`;

export const ChartLegendTd = styled.td`
  padding-right: 15px;
  font-size: 10px;
`;

export const FilterDiv = styled.div`
  margin-left: 30px;
  flex: 1;
  display: flex;
  justify-content: flex-end;
`;

export const DateDiv = styled.div`
  margin-left: 30px;
  flex-wrap: wrap;
`;

export const FilterSelectWrapper = styled.div`
  background: url('/static/images/select-arrow.svg') no-repeat calc(100% - 10px) #f5f6fa;
  background-size: 12px 12px;
  display: flex;
  width: 150px;
  height: 30px;
`;

export const FilterSelect = styled.select`
  background: transparent;
  -moz-appearance: none;
  -webkit-appearance: none;
  padding-left: 10px;
  flex: 1;
  border: none;
`;

export default class Savings extends Component {
  constructor(props) {
    super(props);
    this.onFilterChange = this.onFilterChange.bind(this);
  }

  componentDidMount() {
    const { getSavings, clientId } = this.props;
    getSavings(clientId);
  }

  onFilterChange(event) {
    this.props.updateChartFilter(event.target.value);
  }

  render() {
    const { savings, filters } = this.props;
    const currentMonth = new Date().getMonth();
    const { data, filter } = savings;

    const sum = data.reduce((acc, s) => acc + parseFloat(s[filter]), 0);
    const chartDataSet = data.map(s => ({
      ...s,
      percentOfSum: (parseFloat(s[filter]) / sum) * 100,
    }));
    const currentMonthData = data.find(s => s.month === currentMonth + 1);

    return (
      <Wrapper>
        <WrapperHeader>
          <div>
            <Title>Net {filter}</Title>
            <SavingsTable>
              <tbody>
                <tr>
                  <ChartLegendTd>
                    {getLongMonth(currentMonth)} {filter}
                  </ChartLegendTd>
                  <td>${currentMonthData ? Number(currentMonthData[filter]).toLocaleString('en-EN') : 0}</td>
                </tr>
                <tr>
                  <ChartLegendTd>Year to Date {filter}</ChartLegendTd>
                  <td>${Number(sum).toLocaleString('en-EN')}</td>
                </tr>
              </tbody>
            </SavingsTable>
          </div>
          <FilterDiv>
            <FilterSelectWrapper>
              <FilterSelect onChange={this.onFilterChange}>
                {filters.map(item => (
                  <option value={item} key={item}>
                    Monthly {item}
                  </option>
                ))}
              </FilterSelect>
            </FilterSelectWrapper>
          </FilterDiv>
          <DateDiv>
            <FilterSelectWrapper>
              <FilterSelect>
                <option value="dec2018">December 2018</option>
              </FilterSelect>
            </FilterSelectWrapper>
          </DateDiv>
        </WrapperHeader>
        <SavingsChart savings={chartDataSet} filter={filter} />
      </Wrapper>
    );
  }
}

Savings.propTypes = {
  savings: PropTypes.shape({
    data: PropTypes.arrayOf(
      PropTypes.shape({
        month: PropTypes.number.isRequired,
        savings: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      }),
    ),
  }).isRequired,
  getSavings: PropTypes.func.isRequired,
  clientId: PropTypes.number.isRequired,
  filters: PropTypes.arrayOf(PropTypes.string).isRequired,
  updateChartFilter: PropTypes.func.isRequired,
};

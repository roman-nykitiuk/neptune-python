import React, { Component } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import Plot from '@/react-plotly.js';
import { colorOf, capitalizeFirstLetter } from '@/utils';

const Wrapper = styled.div`
  height: 250px;
`;

export default class Savings extends Component {
  constructor(props) {
    super(props);

    const tickfont = {
      size: 11,
      color: 'rgb(163, 166, 180)',
    };

    this.data = {
      type: 'bar',
      width: 0.4,
      hoverinfo: 'text',
    };
    this.layout = {
      margin: { l: 50, t: 30, r: 50, b: 30, pad: 0 },
      yaxis: {
        tickformat: '$.0f',
        tickfont,
      },
      xaxis: {
        tickfont,
      },
      autosize: true,
    };
    this.config = { displayModeBar: false, responsive: true };
  }

  render() {
    const { savings, filter } = this.props;
    const x = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
    const y = [];
    const color = [];
    const text = [];
    x.forEach((month, index) => {
      const sav = savings.find(s => s.month === index + 1);
      const value = sav ? sav[filter] : 0;
      y.push(value);
      color.push(colorOf(sav && sav.percentOfSum));
      text.push(`${capitalizeFirstLetter(filter)} $${Number(value).toLocaleString('en-EN')}`);
    });
    const data = {
      ...this.data,
      x,
      y,
      text,
      marker: { color },
    };

    return (
      <Wrapper>
        <Plot
          data={[data]}
          layout={this.layout}
          config={this.config}
          useResizeHandler
          style={{ width: '100%', height: '100%' }}
        />
      </Wrapper>
    );
  }
}

Savings.propTypes = {
  savings: PropTypes.arrayOf(
    PropTypes.shape({
      month: PropTypes.number.isRequired,
      percentOfSum: PropTypes.number.isRequired,
      savings: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      percent: PropTypes.string.isRequired,
      spend: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    }),
  ).isRequired,
  filter: PropTypes.string.isRequired,
};

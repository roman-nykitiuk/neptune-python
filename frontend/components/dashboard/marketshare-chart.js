import React, { Component } from 'react';
import Plot from '@/react-plotly.js';
import PropTypes from 'prop-types';

export default class MarketshareChart extends Component {
  constructor(props) {
    super(props);
    this.data = {
      type: 'pie',
      hole: 0.4,
      textinfo: 'percent',
      hoverinfo: 'label+text+percent',
      textfont: { color: '#fff', size: 10 },
      sort: false,
      marker: {
        colors: [
          'rgb(13, 82, 162)',
          'rgb(44, 109, 186)',
          'rgb(64, 134, 215)',
          'rgb(121, 174, 235)',
          'rgb(200, 200, 230)',
          'rgb(75, 0, 130)',
          'rgb(0, 0, 205)',
          'rgb(70, 130, 180)',
          'rgb(0, 191, 255)',
          'rgb(121, 174, 235)',
          'rgb(173, 216, 230)',
          'rgb(69, 21, 113)',
        ],
      },
    };
    this.layout = {
      width: 250,
      height: 250,
      margin: { l: 20, t: 20, r: 20, b: 20, pad: 0 },
      showlegend: false,
    };
    this.config = { displayModeBar: false };
  }

  render() {
    const { marketshare } = this.props;
    const additionalData = { labels: [], values: [], text: [] };
    marketshare.forEach((m, index) => {
      additionalData.labels[index] = m.name;
      additionalData.values[index] = m.spend;
      additionalData.text[index] = `$${Number(m.spend).toLocaleString('en-EN')}<br />${m.units} units`;
    });
    const data = {
      ...this.data,
      ...additionalData,
    };
    return (
      <div>
        <Plot data={[data]} layout={this.layout} config={this.config} />
      </div>
    );
  }
}

MarketshareChart.propTypes = {
  marketshare: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
      spend: PropTypes.string,
      units: PropTypes.number,
    }),
  ).isRequired,
};

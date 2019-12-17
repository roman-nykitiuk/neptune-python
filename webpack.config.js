var path = require('path');
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  context: __dirname,
  entry: './frontend/index.js',
  output: {
    path: path.resolve(__dirname, 'assets/bundles/'),
    filename: 'frontend-[hash].js',
    publicPath: '/static/bundles/',
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: [{ loader: 'babel-loader' }, { loader: 'eslint-loader' }],
      },
      {
        test: /\.css$/,
        use: [{ loader: 'style-loader' }, { loader: 'css-loader' }],
      },
    ],
  },
  plugins: [new BundleTracker({ filename: './webpack-stats.json' })],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'frontend/'),
    },
  },
};

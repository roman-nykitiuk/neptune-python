const path = require('path');
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var webpackConfig = require('./webpack.config');

module.exports = Object.assign({}, webpackConfig, {
  context: __dirname,
  mode: 'development',
  entry: [
    'webpack-dev-server/client?http://localhost:3000',
    'webpack/hot/dev-server',
    './frontend/index'
  ],
  output: {
    path: path.resolve(__dirname, 'assets/bundles/'),
    filename: 'frontend.js',
    // Tell django to use this URL to load packages and not use STATIC_URL
    publicPath: 'http://localhost:3000/assets/bundles/',
  },
  plugins: webpackConfig.plugins.concat([
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NoEmitOnErrorsPlugin(), // don't reload if there is an error
    new webpack.NamedModulesPlugin(),
  ]),
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'frontend/'),
    },
  },
});

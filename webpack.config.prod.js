var webpackConfig = require('./webpack.config');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

module.exports = env => {
  const additionalPlugins = [];
  if (env && env.track === 'true') {
    additionalPlugins.push(new BundleAnalyzerPlugin());
  }
  return Object.assign({}, webpackConfig, {
    plugins: webpackConfig.plugins.concat(additionalPlugins),
  });
};

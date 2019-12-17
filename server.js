var webpack = require('webpack');
var WebpackDevServer = require('webpack-dev-server');
var config = require('./webpack.config.dev');

const options = {
  publicPath: config.output.publicPath,
  hot: true,
  inline: true,
  historyApiFallback: true,
  host: 'localhost',
  headers: { 'Access-Control-Allow-Origin': '*' }
};

new WebpackDevServer(webpack(config), options)
  .listen(3000, 'localhost', function (err, result) {
    if (err) {
      console.log(err);
    }

    console.log('Listening at localhost:3000');
});

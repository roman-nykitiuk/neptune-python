#!/usr/bin/env node

/*
  This script is an alternative solution of ruby lib https://github.com/okkez/coveralls-lcov
  to convert frontend coverage report in lcov format into json format processable by Coveralls.io
 */
var fs = require('fs');
var index = require('./node_modules/coveralls/index');

process.stdin.resume();
process.stdin.setEncoding('utf8');

var input = '';

process.stdin.on('data', function(chunk) {
  input += chunk;
});

process.stdin.on('end', function() {
  index.convertLcovToCoveralls(input, {}, function(err, postData) {
    if (err) {
      throw err;
    }

    fs.writeFile('./coverage/coveralls-frontend.json', JSON.stringify(postData), err => {
      if (err) {
        console.error(err);
        return;
      }
      console.log('File "./coverage/coverage-frontend.json" has been created');
    });
  });
});

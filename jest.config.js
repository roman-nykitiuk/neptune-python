module.exports = {
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/frontend/$1',
  },
  setupTestFrameworkScriptFile: '<rootDir>/setupTests.js',
  testURL: 'http://localhost',
  coverageDirectory: '.nyc_output'
};

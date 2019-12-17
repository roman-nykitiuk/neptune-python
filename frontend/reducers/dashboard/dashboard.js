import { combineReducers } from 'redux';
import marketshare from './marketshare';
import repCases from './rep-cases';
import savings from './savings';
import bulkInventory from './bulk-inventory';

export default combineReducers({
  marketshare,
  repCases,
  savings,
  bulkInventory,
});

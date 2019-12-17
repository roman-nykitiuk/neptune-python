import { connect } from 'react-redux';
import MarketShare from '@/components/dashboard/marketshare';
import getMarketShare from '@/actions/marketshare-actions';

const mapStateToProps = state => ({
  marketshare: state.dashboard.marketshare,
});

const mapDispatchToProps = {
  getMarketShare,
};

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(MarketShare);

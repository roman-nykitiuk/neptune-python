import styled from 'styled-components';
import { Section } from '../dashboard-styles';

export const Wrapper = styled.div`
  flex: 0 0 33.33%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
`;

export const SubWrapper = styled(Section)``;

export const Total = styled.h1`
  font-size: 38px;
  font-weight: 600;
  color: #4a4a4a;
  margin: 0;
  margin-top: 16px;
`;

const Value = styled.p`
  font-size: 13px;
  font-weight: 600;
`;
export const DownValue = styled(Value)`
  color: #fb432a;
`;

export const UpValue = styled(Value)`
  color: #76be43;
`;

export default Wrapper;

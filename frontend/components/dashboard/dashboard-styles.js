import styled from 'styled-components';

export const Wrapper = styled.div`
  padding: 23px 16px 23px 23px;
`;

const Row = styled.div`
  display: flex;
  justify-content: space-between;
`;
export const FirstRow = styled(Row)`
  margin-bottom: 15px;
`;

export const SecondRow = styled(Row)`
  flex-wrap: wrap;
  @media only screen and (max-width: 1600px) {
    > div {
      margin-right: 0;
      margin-bottom: 10px;
    }
  }
`;

export const Title = styled.h4`
  color: #0a488f;
  font-size: 13px;
  font-weight: bold;
  margin: 0;
  text-align: left;
`;

export const Section = styled.div`
  padding: 15px 22px;
  background-color: #ffffff;
  box-shadow: 0 2px 6px 0 rgba(28, 36, 78, 0.15);
`;

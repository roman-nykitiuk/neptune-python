import styled from 'styled-components';

export const Wrapper = styled.div`
  display: flex;
  height: 100vh;
`;

export const LeftPanel = styled.div`
  max-width: 50%;
  flex: 0 0 50%;
  padding: 12vh 6vw;
  background-image: url('/static/images/banner.png');
  background-size: cover;
  background-repeat: no-repeat;

  > img {
    width: 300px;
    margin-bottom: 30px;
  }
  > p {
    font-size: 28px;
    font-weight: 600;
    color: #0a488f;
    margin: 0.2em 0;
  }
`;

export const RightPanel = styled.div`
  max-width: 50%;
  flex: 0 0 50%;
  background-color: #0a488f;
  display: flex;
  align-items: center;
`;

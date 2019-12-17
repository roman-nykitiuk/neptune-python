import styled from 'styled-components';
import { Link } from 'react-router-dom';

export const MenuWrapper = styled.div`
  max-width: 260px;
  width: 260px;
  background-color: #0a488f;
  position: absolute;
  top: 70px;
  bottom: 0;
  padding: 29px;
`;

export const MenuItem = styled(Link)`
  display: block;
  color: #fff;
  font-size: 16px;
  display: flex;
  align-items: center;
  text-decoration: none;
  padding: 15px 0;
  margin-bottom: 24px;

  > span {
    margin-left: 15px;
  }

  > img {
    width: 20px;
  }
`;

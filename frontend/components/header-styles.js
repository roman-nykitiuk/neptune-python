import styled from 'styled-components';

export const Navbar = styled.div`
  background-color: white;
  display: flex;
  height: 70px;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.1);
`;

export const Branding = styled.a`
  width: 260px;
  display: inline-block;
  border-right: solid 1px #f1f1f3;
  height: 100%;
  vertical-align: middle;
  display: flex;
  justify-content: center;
  align-items: center;
  img {
    width: 210px;
  }
`;

export const SearchBox = styled.div`
  flex: 1;
  padding: 15px;
  position: relative;
`;

export const SearchInput = styled.input`
  border: 0;
  width: 100%;
  padding-left: 30px;
  outline: none;
`;

export const SearchIcon = styled.img`
  position: absolute;
`;

export const UserNav = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-right: 16px;
`;

export const UserInfo = styled.p`
  display: flex;
  align-items: center;
  span {
    color: #a3a6b4;
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
  }
`;

export const UserIcon = styled.img`
  margin-left: 16px;
`;

export const MarketshareWrapper = styled.div`
  background: #fff;
  padding: 5px 22px;
  overflow: hidden;
  p {
    color: #0a488f;
    font-size: 13px;
    font-weight: bold;
  }
`;

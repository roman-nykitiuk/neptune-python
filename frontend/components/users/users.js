import styled from 'styled-components';
import EditTable from '@/components/common/edit-table';
import React, { Component } from 'react';
import { Wrapper } from '../dashboard/dashboard-styles';

export const StyledTable = styled(EditTable)`
  flex: 1;
  min-width: 300px;
  border: 3px black;
`;

export default class Dashboard extends Component {
  render() {
    const titles = {
      name: 'Name',
      email: 'E-mail',
      role: 'Role',
      org: 'Organization',
      scec: 'Speciality',
      eng: 'Engagement',
      act: 'Actions',
    };
    const rows = [
      {
        name: 'Name',
        email: 'E-mail',
        role: 'Role',
        org: 'Organization',
        scec: 'Speciality',
        eng: 'Engagement',
        act: 'Actions',
      },
      {
        name: 'Name',
        email: 'E-mail',
        role: 'Role',
        org: 'Organization',
        scec: 'Speciality',
        eng: 'Engagement',
        act: 'Actions',
      },
    ]; // TODO: Users data
    return (
      <Wrapper>
        <StyledTable titles={titles} rows={rows} />
      </Wrapper>
    );
  }
}

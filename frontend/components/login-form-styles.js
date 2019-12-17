import styled from 'styled-components';

export const FormWrapper = styled.div`
  width: 100%;
  max-width: 400px;
  margin: auto;

  > h2 {
    font-size: 28px;
    font-weight: 600;
    color: white;
    margin-bottom: 45px;
  }
`;

export const Input = styled.input`
  display: block;
  width: 100%;
  padding: 0.375rem 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  color: white;
  background-color: #0a488f;
  border: 0;
  border-bottom: 1px solid white;
  ::placeholder {
    color: white;
  }
`;

export const SubmitButton = styled(Input)`
  margin-top: 54px;
  display: inline-block;
  width: 100%;
  background-color: white;
  color: #0a488f;
  font-weight: 600;
  font-size: 14px;
`;

export const FormGroup = styled.div`
  margin-bottom: 1rem;
`;

export const ErrorMessage = styled.p`
  color: #e23f65;
  font-weight: 600;
  background-color: white;
  border-color: #f5c6cb;
  padding: 0.75rem 1.25rem;
  margin-bottom: 1rem;
  border: 1px solid transparent;
`;

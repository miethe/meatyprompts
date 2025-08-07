jest.mock('../../CodeEditor', () => {
  const React = require('react');
  return {
    __esModule: true,
    default: (props: any) => React.createElement('textarea', { 'data-testid': 'codemirror', readOnly: props.readOnly }),
    LANGUAGE_OPTIONS: ['plaintext'],
  };
});

jest.mock('../../form/TagInput', () => {
  const React = require('react');
  return () => React.createElement('div');
});
jest.mock('../../form/CreatableMultiSelect', () => {
  const React = require('react');
  return () => React.createElement('div');
});

jest.mock('../../../contexts/PromptContext', () => ({
  usePrompt: () => ({ createPrompt: jest.fn() }),
}));

jest.mock('../../../contexts/LookupContext', () => ({
  useLookups: () => ({
    lookups: { target_models: [], providers: [], integrations: [], use_cases: [], loading: false },
    addLookup: jest.fn(),
  }),
}));

jest.mock('../../../contexts/FieldHelpContext', () => ({
  useFieldHelp: () => ({
    help: {
      target_models: 'Target models help',
      providers: 'Providers help',
      integrations: 'Integrations help',
    },
    loading: false,
  }),
}));

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ManualPromptForm from '../ManualPromptForm';

describe('ManualPromptForm', () => {
  it('renders field help tooltips', () => {
    render(React.createElement(ManualPromptForm, { onClose: () => {} }));
    expect(screen.getAllByLabelText('Information')).toHaveLength(3);
    expect(screen.getAllByTestId('codemirror')).toHaveLength(1);
    fireEvent.click(screen.getByText('Advanced'));
    expect(screen.getAllByTestId('codemirror')).toHaveLength(2);
  });
});

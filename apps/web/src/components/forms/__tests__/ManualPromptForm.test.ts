import React from 'react';
import { render, screen } from '@testing-library/react';
import ManualPromptForm from '../ManualPromptForm';

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

describe('ManualPromptForm', () => {
  it('renders field help tooltips', () => {
    render(React.createElement(ManualPromptForm, { onClose: () => {} }));
    expect(screen.getByTitle('Target models help')).toBeInTheDocument();
    expect(screen.getByTitle('Providers help')).toBeInTheDocument();
    expect(screen.getByTitle('Integrations help')).toBeInTheDocument();
  });
});

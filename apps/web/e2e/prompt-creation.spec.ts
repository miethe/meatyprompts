describe('Prompt Creation v1 (Legacy)', () => {
  // Keeping the old test as a reference or for regression
  it('should allow a user to create a new prompt manually', () => {
    // ... old test code
  });
});

describe('Prompt Creation v2 & Filtering', () => {
  beforeEach(() => {
    // Mock all the necessary API calls before each test
    cy.intercept('GET', '/api/v1/lookups/models', { body: [{ id: '1', value: 'gpt-4' }] }).as('getModels');
    cy.intercept('GET', '/api/v1/lookups/tools', { body: [] }).as('getTools');
    cy.intercept('GET', '/api/v1/lookups/platforms', { body: [{ id: '1', value: 'web' }] }).as('getPlatforms');
    cy.intercept('GET', '/api/v1/lookups/purposes', { body: [] }).as('getPurposes');
    cy.intercept('POST', '/api/v1/lookups/tools', { body: { id: '2', value: 'new-tool' } }).as('createTool');

    cy.intercept('POST', '/api/v1/prompts', {
      statusCode: 201,
      body: { id: 'new-prompt-id', version: 1, title: 'My V2 Prompt' /* ... other fields */ }
    }).as('createPrompt');

    cy.intercept('GET', '/api/v1/prompts*', {
      body: [{ id: 'new-prompt-id', version: 1, title: 'My V2 Prompt', models: ['gpt-4'], tools: ['new-tool'], purpose: ['testing'] }]
    }).as('getPrompts');

    cy.visit('/prompts'); // Assuming this is the main prompts page
    cy.wait(['@getModels', '@getTools', '@getPlatforms', '@getPurposes', '@getPrompts']);
  });

  it('allows creating, filtering, and editing a prompt with rich metadata', () => {
    // 1. Open the creation modal
    cy.get('button').contains('New Prompt').click();
    cy.get('button').contains('Manual').click();

    // 2. Fill out the form, creating a new tool
    cy.get('input[name="title"]').type('My V2 Prompt');
    cy.get('textarea[name="body"]').type('This is the body.');

    // Interact with react-select for models
    cy.get('label:contains("Models")').next().find('input').type('gpt-4{enter}');

    // Interact with react-select to create a new tool
    cy.get('label:contains("Tools")').next().find('input').type('new-tool{enter}');
    cy.wait('@createTool');

    // 3. Submit the form
    cy.get('button').contains('Submit').click();
    cy.wait('@createPrompt');

    // 4. Filter the list to find the new prompt
    cy.get('button').contains('Filters').click();
    cy.get('label:contains("Tools")').next().find('input').type('new-tool{enter}');
    cy.get('button').contains('Apply Filters').click();
    cy.wait('@getPrompts'); // Wait for the filtered list

    // 5. Verify the card is visible and open the detail modal
    cy.get('.prompt-card').should('contain', 'My V2 Prompt').click();
    cy.get('h2').should('contain', 'My V2 Prompt'); // Check modal title

    // 6. Edit the prompt
    cy.intercept('PUT', '/api/v1/prompts/new-prompt-id', {
      statusCode: 200,
      body: { id: 'new-prompt-id', version: 1, title: 'My Edited V2 Prompt' }
    }).as('updatePrompt');

    cy.get('button').contains('Edit').click();
    cy.get('input[id="title"]').clear().type('My Edited V2 Prompt');
    cy.get('button').contains('Save Changes').click();
    cy.wait('@updatePrompt');

    // 7. Verify the card has updated
    cy.get('.prompt-card').should('contain', 'My Edited V2 Prompt');
  });
});

describe('Prompt Creation', () => {
  it('should allow a user to create a new prompt manually', () => {
    cy.visit('/');
    cy.get('button').contains('New Prompt').click();
    cy.get('button').contains('Manual').click();

    cy.get('input[name="title"]').type('My New Prompt');
    cy.get('textarea[name="body"]').type('This is the prompt text.');
    cy.get('select[name="models"]').select('gpt-3.5-turbo');

    cy.intercept('POST', '/api/v1/prompts', {
      statusCode: 201,
      body: {
        id: 'a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6',
        title: 'My New Prompt',
        purpose: '',
        models: ['gpt-3.5-turbo'],
        tools: [],
        tags: [],
        body: 'This is the prompt text.',
        visibility: 'private',
        version: 1,
        createdAt: new Date().toISOString(),
        prompt_id: 'p1q2r3s4-t5u6-v7w8-x9y0-z1a2b3c4d5e6',
      },
    }).as('createPrompt');

    cy.get('button').contains('Submit').click();

    cy.wait('@createPrompt');

    cy.get('.prompt-card').first().should('contain', 'My New Prompt');
  });
});

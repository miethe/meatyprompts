# Prompts Library

This library collects reusable prompt blocks for AI agents.  Each block
describes the inputs expected and the structure of the output.

## PRD from Idea

*Inputs*: short idea, user segments, jobs to be done, constraints.
*Output*: A Product Requirements Document with problem statement, scope,
acceptance criteria, and risks.  Do not fabricate APIs; list unknown
information as assumptions.

## Implementation Plan

*Inputs*: PRD.  
*Output*: Milestones, tasks, dependencies, test strategy, and success
metrics.  Be explicit about ordering and parallelism.

## User Story Template

Use the INVEST format: Independent, Negotiable, Valuable, Estimable,
Small, Testable.  Include acceptance criteria, non‑functional
requirements, edge cases, and a high‑level test outline.

## ADR Template

Title, context, options considered, decision, consequences, and rollback
strategy.  Keep ADRs concise and link to relevant documentation.

## Test Generation

*Inputs*: User story.  
*Output*: Jest tests (for mobile/web) and pytest tests (for API).  Include
boundary cases and edge conditions.  Follow existing test patterns.

## Release Notes

Generate release notes by summarising merged PRs grouped by labels
(features, fixes, chores, docs).  Format them for inclusion in the
CHANGELOG.  Cite PR numbers and authors where appropriate.
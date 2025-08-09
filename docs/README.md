# MeatyPrompts Documentation Hub

Welcome to the project documentation for MeatyPrompts. This directory serves as the master guide to finding, creating, and maintaining all project-related documentation. Its purpose is to ensure that information is organized, accessible, and evolves alongside the codebase.

**The most important document for any new team member is [`guides/PROJECT_OVERVIEW.md`](guides/PROJECT_OVERVIEW.md). Please start there.**

## Documentation Philosophy

1. **Living Documents:** Documentation is not a one-time task. It must evolve with the codebase. Every pull request that changes behavior, adds a feature, or alters architecture must include corresponding documentation updates.
2. **Audience-Centric:** Information is structured and written for its intended audience. We recognize the different needs of Developers, Product Managers, System Administrators, and End Users.
3. **Single Source of Truth:** This directory is the canonical source for project knowledge. Avoid documenting project details in external tools or personal notes.

## Directory Structure

Our documentation is organized by function and audience.

```graphql
docs/
├── README.md               # You are here. The master guide to all documentation.
│
├── guides/                 # 📖 How-to guides, tutorials, and onboarding for the team.
│   ├── PROJECT_OVERVIEW.md # THE STARTING POINT. Tech, product, and architecture summary.
│   ├── QUICK_REFERENCE.md  # "Cheat sheet" for common dev tasks and repo layout.
│   ├── DEVELOPMENT_GUIDE.md# Step-by-step for setting up a local dev environment.
│   └── AGENT_GUIDE.md      # Specialized instructions for AI development agents.
│
├── architecture/           # 🏛️ High-level architectural decisions, diagrams, and patterns.
│   ├── ADRs/               # Formal Architectural Decision Records (ADRs).
│   └── diagrams/           # System diagrams (C4, sequence, etc.).
│
├── features/               # 💡 In-depth developer guides for specific application features.
│   ├── prompt_engine.md    # Deep dive into the Model Adapter and Prompt Engine.
│   └── collections.md      # Implementation details for the Collections feature.
│
├── api/                    # ↔️ API specifications, endpoint examples, and data contracts.
│   └── openapi.json        # The machine-readable OpenAPI/Swagger specification.
│
├── ops/                    # ⚙️ Operational documentation (CI/CD, deployment, observability).
│   ├── deployment.md       # Guides on deploying the application to different environments.
│   └── monitoring.md       # Details on our logging, tracing, and alerting setup.
│
├── product/                # 📈 Product management, planning, and strategic documents.
│   ├── roadmap.md          # High-level product roadmap and release phases.
│   ├── user_stories/       # Epics and user stories for upcoming features.
│   └── research/           # Exploratory research, competitive analysis, and PoCs.
│
├── user_guides/            # 👤 Content for end-users. This is the source for our future public wiki/help center.
│   ├── getting_started.md  # First steps for a new user.
│   └── advanced_search.md  # How to use search filters and operators.
│
└── archive/                # 🗄️ Deprecated or superseded documents.
```

---

## Directory Deep Dive

### `guides/`

- **Purpose**: To provide practical, hands-on instructions for the internal team. If you need to explain *how* to do something related to working on the project, it belongs here.
- **Audience**: **All Team Members** (Developers, PMs, Designers).
- **When to Update**: When the development process, environment setup, or high-level project structure changes.

### `architecture/`

- **Purpose**: To document the *why* behind our most significant technical choices. It provides the high-level context for the system's design and evolution.
- **Audience**: **Developers**, **System Administrators**.
- **Contents**:
  - `ADRs/`: **Architectural Decision Records**. Use the provided template for significant, enduring technical decisions (e.g., choosing a database, adopting an auth provider).
  - `diagrams/`: Visual representations of the architecture.
- **When to Update**: When a major architectural decision is made or when a diagram is needed to clarify a complex interaction.

### `features/`

- **Purpose**: To provide detailed technical documentation for the implementation of specific product features. This is where you explain the "how it works" under the hood.
- **Audience**: **Developers**.
- **When to Update**: When building a new feature or making significant changes to an existing one. Create a new markdown file for each major feature.

### `api/`

- **Purpose**: To provide a complete, unambiguous reference for the MeatyPrompts API. This is the contract between the frontend and backend.
- **Audience**: **Developers** (both frontend and backend).
- **When to Update**: This should be automatically updated whenever an API endpoint is added, changed, or removed, by exporting from our FastAPI application.

### `ops/`

- **Purpose**: To document operational procedures, including infrastructure, CI/CD, and observability.
- **Audience**: **System Administrators**, **DevOps**, **Developers**.
- **When to Update**: When changing the build process, deployment scripts, hosting infrastructure, or monitoring tools.

### `product/`

- **Purpose**: To track the project's strategic direction, planning artifacts, and research.
- **Audience**: **Product Managers**, **Stakeholders**, **All Team Members** (for context).
- **When to Update**: During sprint planning, roadmap reviews, or when conducting market/user research.

### `user_guides/`

- **Purpose**: To create clear, non-technical documentation intended for **end-users**. This content is the source of truth for our public-facing knowledge base, help center, or wiki.
- **Audience**: **End Users**.
- **When to Update**: When a new user-facing feature is released, or an existing one changes in a way that affects how users interact with it.

---

## How to Document Your Work: A Checklist

Use this table to determine where to find or place documentation for a given task.

| If you are...                                       | Then you should...                                                                                                                      |
| :-------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| **Joining the project or need a refresher**         | **Read** [`guides/PROJECT_OVERVIEW.md`](guides/PROJECT_OVERVIEW.md) and [`guides/DEVELOPMENT_GUIDE.md`](guides/DEVELOPMENT_GUIDE.md) first. |
| **Making a significant architectural decision**     | **Create** a new ADR in [`architecture/ADRs/`](architecture/ADRs/).                                                                      |
| **Adding or changing an API endpoint**              | **Ensure** the auto-generated `api/openapi.json` is updated as part of your PR.                                                         |
| **Implementing a new, complex feature**             | **Create** a new technical deep-dive in [`features/`](features/).                                                                       |
| **Implementing a feature that users need to learn** | **Create or update** a guide in [`user_guides/`](user_guides/).                                                                         |
| **Changing the build or deployment process**        | **Update** the relevant document in [`ops/`](ops/).                                                                                     |
| **Modifying the database schema**                   | **Explain** the rationale in your feature guide (`features/`) or an ADR if it's a major change.                                         |
| **Planning a new Epic or Sprint**                   | **Add** user stories or planning documents to [`product/`](product/).                                                                   |
| **Exploring a new technology or idea**              | **Add** your findings to the [`product/research/`](product/research/) directory.                                                         |
| **Deprecating a feature or guide**                  | **Move** the outdated document to the [`archive/`](archive/) directory.                                                                  |

# Layered vs Monolithic

## 1. Impact of Each Architectural Style

---

### Layered Architecture (Original)

The original codebase separated concerns across five distinct files: `models.py`, `database.py`, `service.py`, `controller.py`, and `server.py`, each representing a dedicated layer.

**Maintainability**
Each layer has a single responsibility. Changes to database logic are isolated in `database.py`, business rules in `service.py`, and so on. A developer can locate and modify a specific concern without reading the entire codebase.

**Testability**
Individual layers can be unit tested in isolation. The `ContactRepository`, `ContactService`, and `ContactController` can each be instantiated and tested independently, and dependencies can be mocked at layer boundaries.

**Scalability**
Layers can be extracted into separate services or processes independently as the system grows. For example, the repository layer could be swapped for a remote data store without touching the service or controller layers.

**Readability**
The structure is self-documenting. A new developer can infer what each file does from its name and layer position alone, and the relationships between layers are explicit.

**Reusability**
Individual layers, particularly `ContactService` and `ContactRepository`, can be reused by different entry points (e.g., a CLI tool, a background job, or a different HTTP framework) without modification.

**Verbosity / Overhead**
The primary cost is that five files and multiple class instantiations are required to serve a single request. For a small application, this indirection adds complexity without meaningful benefit at the current scale.

---

### Monolithic Architecture (New)

The converted codebase consolidates everything into a single `server.py` file, with module-level functions replacing the layered classes.

**Simplicity**
There is one file to open, read, and run. There are no import chains to trace, no constructor injections to follow, and no layers to context-switch between.

**Onboarding Speed**
A developer new to the project can understand the entire system by reading one file from top to bottom. This is a meaningful advantage for small or short-lived projects.

**Maintainability**
As the application grows, the single file becomes harder to navigate. Adding new entities (e.g., `User`, `Product`) means the file grows without a natural way to separate concerns. Changes to unrelated features occupy the same file, increasing the chance of merge conflicts in team environments.

**Testability**
Module-level functions are harder to mock and isolate than class-based layers. Testing the HTTP handler requires the database layer to also be exercised unless additional effort is invested in patching global functions.

**Coupling**
All concerns, HTTP handling, business logic, and data access, are tightly coupled. A change to the database schema, for example, may require touching code that is logically part of the HTTP layer.

**Performance**
At runtime, both architectures perform identically for this application. The layered version introduces no meaningful overhead since class instantiation is negligible.

---

## 2. Comparison and Trade-offs

| Quality | Layered | Monolithic |
|---|---|---|
| Maintainability | High — changes are isolated per layer | Low at scale — everything is in one place |
| Testability | High — layers can be mocked independently | Moderate — module functions are harder to isolate |
| Readability (small scale) | Moderate — requires tracing across files | High — linear, top-to-bottom reading |
| Readability (large scale) | High — structure enforces organisation | Low — file grows unwieldy |
| Reusability | High — service/repo layers are portable | Low — logic is entangled with HTTP handling |
| Onboarding | Moderate — must understand layer conventions | High — single file, no conventions needed |
| Scalability | High — layers can evolve independently | Low — tightly coupled, hard to decompose |
| Boilerplate | High — five files, multiple classes | Low — one file, module-level functions |

---

### Key Trade-offs

**Separation vs Simplicity**
The layered architecture pays an upfront cost in file count and indirection to gain long-term separation of concerns. The monolithic version eliminates that cost but defers the complexity problem, it does not remove it. As the application grows, the monolith accumulates the complexity the layered version was designed to prevent.

**Testability vs Convenience**
Layered code is significantly easier to test in isolation because each class can be instantiated with mock dependencies. The monolith requires patching module-level functions or spinning up the full stack, which makes unit testing more cumbersome.

**Right Tool for the Right Scale**
The monolithic architecture is a defensible choice for this application at its current size: four endpoints, one entity, and a simple SQLite backend. The layered architecture is over-engineered for that scope. However, the layered design becomes the better choice the moment a second entity is added, a second developer joins, or the codebase needs automated tests, because the structural investment has already been made.

**Which is 'Better'**
Neither architecture is universally correct. The layered approach optimises for growth, collaboration, and testability at the cost of initial complexity. The monolithic approach optimises for speed and simplicity at the cost of long-term maintainability. The appropriate choice depends on the expected lifespan, team size, and growth trajectory of the system.

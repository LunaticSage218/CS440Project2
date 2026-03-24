# Layered vs Peer-to-Peer

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

### Peer-to-Peer Architecture (New)

The converted codebase removes the central server entirely. Each running instance acts as both a client and a server, maintaining its own local database while synchronizing updates with other peers over HTTP.

**Simplicity**  
The system is no longer simple in structure. Instead of one file or one server, multiple running instances must be coordinated. Understanding behavior now requires reasoning about interactions between peers rather than a single execution flow.

**Onboarding Speed**  
A developer new to the project must understand not only the code but also how multiple peers communicate and synchronize. This increases the learning curve compared to centralized architectures.

**Maintainability**  
As the application grows, maintaining the system becomes more difficult due to distributed concerns. Changes to synchronization logic or communication protocols can impact all peers, and debugging requires tracking behavior across multiple nodes.

**Testability**  
Testing is more complex because functionality depends on interactions between multiple running peers. Unit testing is less straightforward, and integration testing requires simulating or running multiple instances simultaneously.

**Coupling**  
While local CRUD logic remains modular, the system introduces coupling through network communication. Each peer depends on other peers for synchronization, creating implicit dependencies between instances.

**Performance**  
Local operations remain fast, but write operations introduce additional overhead due to synchronization. Each create, update, or delete must be propagated to other peers, increasing latency compared to centralized systems.

---

## 2. Comparison and Trade-offs

| Quality | Layered | Peer-to-Peer |
|---|---|---|
| Maintainability | High — changes are isolated per layer | Low — distributed logic increases complexity |
| Testability | High — layers can be mocked independently | Low — requires multi-node testing |
| Readability (small scale) | Moderate — requires tracing across files | Low — must understand multiple interacting peers |
| Readability (large scale) | High — structure enforces organisation | Low — distributed behavior adds complexity |
| Reusability | High — service/repo layers are portable | Moderate — core logic reusable, networking is not |
| Onboarding | Moderate — must understand layer conventions | Low — requires understanding distributed systems |
| Scalability | High — layers can evolve independently | High — horizontal scaling via peers |
| Availability | Low — single server dependency | High — no single point of failure |
| Consistency | Strong — single source of truth | Eventual — synchronization required |
| Boilerplate | High — five files, multiple classes | Moderate — networking and sync logic required |

---

### Key Trade-offs

**Separation vs Simplicity**  
The layered architecture pays an upfront cost in file count and indirection to gain long-term separation of concerns. The peer-to-peer architecture removes centralization entirely but replaces simplicity with distributed coordination. Instead of preventing complexity, it shifts complexity into synchronization and communication between nodes.

**Testability vs Convenience**  
Layered code is significantly easier to test in isolation because each class can be instantiated with mock dependencies. The peer-to-peer system requires running multiple peers or simulating network interactions, making testing more complex and less convenient.

**Right Tool for the Right Scale**  
The peer-to-peer architecture introduces capabilities such as fault tolerance and decentralization, but these are unnecessary for a small application with a single entity and limited endpoints. The layered architecture may feel over-engineered at a small scale, but it provides a strong foundation for growth without introducing distributed complexity.

**Which is 'Better'**  
Neither architecture is universally correct. The layered approach optimises for maintainability, scalability, and testability in a centralized system. The peer-to-peer approach optimises for availability and decentralization but introduces significant complexity. The appropriate choice depends on whether the system prioritizes simplicity and structure or distributed resilience and fault tolerance.
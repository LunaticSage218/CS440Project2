# Layered vs Publish–Subscribe

## 1. Impact of Each Architectural Style

---

### Layered Architecture (Original)
The original codebase follows a traditional request–response model where the user interface communicates with the server through a structured layer system and is organized so that each layer performs a specific role and passes work to the layer below it.

**Maintainability**
Each layer has a single well-defined responsibility. The user interface manages presentation, the server handles HTTP requests, the database layer stores persistent data, and so on. A developer can modify a specific part of the codebase without needing to modify the other layers.

**Testability**
The individual layered system allows each layer to be tested in isolation. The various functions and server logic can all be tested with ease and minimal mocks are needed as there's little dependency or user interfacing required.

**Scalability**
Layered architectures scale well with centralized systems, as individual layers can evolve independently as the system grows. For example, the data storage layer could be replaced with a different database without affecting the user interface or request-handling logic.

**Readability**  
The structure of the system is relatively intuitive, as a developer can likely follow what a layer does by name alone. And because communication follows a simple path, the overall behavior of the application is easy to trace.

**Reusability**  
The system is highly reusable as the logic implemented in the server layer can be reused by different interfaces. For example, the same backend endpoints could support a web client, a mobile application, or a command-line interface.

**Verbosity / Overhead**  
The primary cost is that five files and multiple classes are required to fully serve a single request, addind complexity overhead. And in this case, for such a small application, this adds complexity without meaningful benefit at the project's current scale.

---

### Peer-to-Peer Architecture (New)
The new converted system introduces an event-driven model that communicates through published events rather than direct requests. The server acts as a publisher of events, while connected clients subscribe to those events through a WebSocket connection.

**Decoupling**  
The Publish–subscribe system significantly reduces coupling between components. Publishers do not need to know which or how many clients will receive their messages. As long as the subscribers (clients) listen for the relevant events, the system can develop without tightly linking components together.

**Real-Time Updates**  
This architecture supports real-time communication throught the use of WebSockets. When a change occurs, such as adding or deleting a contact, the server publishes an event that is delivered to all subscribed clients, this allows users to see updates instantly without sending a request to the server.

**Scalability**
Publish–subscribe architectures scale well in environments with many consumers of the same data. A single event can be broadcast to a wide number of subscribers simultaneously. So as the system grow, additional subscribers can be added without modifying the publishing logic.

**Flexibility**
New features can be implemented by subscribing to the existing events. For example, a logging, analytics, or monitoring tool could be added and subscribe to the contact events without altering the server's core logic.

**Complexity**
The event-driven nature introduces additional complexity. Developers must use asynchronous communication, event ordering, and deal with potential race conditions, all of which add more complexity.

**Debugging and Observability**
Tracing behavior becomes more challenging in a publish–subscribe system. Instead of following a single request through layers, developers must track events as they propagate through the system and determine which components reacted to them or didn't react to them. 

---



## 2. Comparison and Trade-offs

| Quality | Layered | Peer-to-Peer |
|---|---|---|
| Maintainability | High — responsibilities are separated by layer | Moderate — decoupling helps, but event flow adds complexity |
| Testability | High — layers can be tested independently | Moderate — requires testing asynchronous events |
| Readability (small scale) | Moderate — flows across files | Moderate — behavior depends on events |
| Readability (large scale) | High — structure compliments clear organization | Moderate — event systems require tracing subscriptions |
| Reusability | High — backend services can support multiple interfaces | High — new subscribers can reuse existing events |
| Onboarding | Moderate — must understand layer conventions | Moderate — requires understanding event-driven systems |
| Scalability | High — layers can be developed independently | High — events can broadcast to many subscribers |
| Coupling | Moderate — layers depend on each other | Low — publishers do not know subscribers |
| Real-time capability | Low — requires polling or refresh | High — updates are pushed to subscribers instantly |
| Boilerplate | High — five files with multiple classes | Moderate — requires publishing, subscription handling, and routing |

---

### Key Trade-offs
**Structured Flow vs Event Flexibility**
Layered architecture prioritizes a clear and predictable flow where requests move sequentially through the system. Publish–subscribe replaces this direct path with event broadcasting, which allows for more flexible communication but makes the execution flow less explicit and harder to trace.

**Synchronous vs Asynchronous Communication**
Layered systems rely mainly on synchronous request–response interactions, in contrast, publish–subscribe architectures are event-driven and asynchronous. This enables real-time updates but introduces additional coordination complexity throughout the system.

**Coupling vs Decoupling**
Layered architectures maintain logical separation but still rely on direct dependencies between layers. Meanwhile, a publish–subscribe architectures reduces those dependencies by allowing publishers and subscribers to operate independently through a shared event channel.

**Which is 'Better'**  
Neither architecture is universally superior. Layered architecture provides clarity, maintainability, and predictable request flow in centralized applications. Publish–subscribe architectures prioritize decoupling, real-time communication, and scalability across multiple clients. The appropriate choice depends on whether the system favors structured request handling or event-driven communication.
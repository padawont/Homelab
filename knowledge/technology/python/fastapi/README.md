# FastAPI

Modern, fast async web framework for building APIs with Python.

## Contents

### Getting Started
- [Installation](./installation.md)
- [First App](./first-app.md)
- [Running Uvicorn](./running-uvicorn.md)

### Routing & Parameters
- [Path Operations](./path-operations.md)
- [Path Parameters](./path-parameters.md)
- [Query Parameters](./query-parameters.md)
- [Path Parameter Validation](./path-parameters-validation.md)
- [Query Parameter String Validation](./query-parameters-str-validation.md)

### Request Body
- [Single Model Body](./request-body-single.md)
- [Multiple Body Params](./request-body-multiple.md)
- [Nested Models](./request-body-nested.md)
- [Field() Validations](./request-body-fields.md)
- [Embed Parameter](./request-body-embed.md)

### Response
- [Response Model](./response-model.md)
- [Response Model Exclude/Include](./response-model-exclude.md)
- [Response Status Code](./response-status-code.md)
- [Response Headers](./response-headers.md)
- [Response Cookies](./response-cookies.md)

### Forms & Files
- [Form Data & File Uploads](./form-data.md)
- [Multiple File Uploads](./form-files-multiple.md)

### Cookies & Headers
- [Cookie Parameters](./cookie-parameters.md)
- [Header Parameters](./header-parameters.md)

### Dependency Injection
- [Dependency Injection Intro](./dependency-injection-intro.md)
- [Dependency Functions](./dependency-functions.md)
- [Dependency Classes](./dependency-classes.md)
- [Sub-Dependencies](./dependency-sub-dependencies.md)
- [Global Dependencies](./dependency-global.md)
- [Dependency Override Testing](./dependency-override-testing.md)

### Middleware
- [Middleware Intro](./middleware-intro.md)
- [CORS Middleware](./middleware-cors.md)
- [Timing/Logging Middleware](./middleware-timing.md)
- [GZip Middleware](./middleware-gzip.md)

### Error Handling
- [Exception Handlers](./exception-handlers.md)
- [HTTPException](./http-exception.md)
- [Custom Exception Responses](./custom-exception-responses.md)
- [Production Error Handling](./error-handling-production.md)

### Background Tasks
- [Background Tasks](./background-tasks.md)
- [Advanced Background Tasks](./background-task-advanced.md)

### Async
- [async def vs def](./async-handlers.md)
- [Blocking I/O](./blocking-io.md)

### Static Files & HTML
- [Static Files](./static-files.md)
- [HTML Response](./html-response.md)

### Routers
- [APIRouter](./routers.md)
- [Router Prefix, Tags, Responses](./routers-prefix.md)
- [Router Dependencies](./routers-dependencies.md)

### Application Lifecycle
- [Lifespan Context Manager](./app-lifecycle.md)
- [Legacy Startup/Shutdown](./startup-shutdown.md)
- [Mounting Sub-Apps](./mounting-sub-apps.md)

### OpenAPI
- [OpenAPI Metadata](./openapi-metadata.md)
- [OpenAPI Tags](./openapi-tags.md)
- [OpenAPI Operation ID](./openapi-operation-id.md)

### Testing
- [TestClient Setup](./testing-testclient-intro.md)
- [TestClient Context Manager](./testing-testclient-call.md)
- [Testing JSON Endpoints](./testing-json-params.md)
- [Testing Query Endpoints](./testing-query-params.md)
- [Testing Form Data](./testing-form-data.md)
- [Testing Authentication](./testing-auth.md)
- [Testing WebSockets](./testing-websockets.md)
- [Async Client](./testing-async-client.md)
- [Dependency Override Patterns](./testing-dependency-overrides.md)

### Streaming
- [StreamingResponse](./streaming-response.md)
- [FileResponse](./streaming-file.md)
- [Server-Sent Events](./streaming-sse.md)
- [FileResponse Headers](./file-response.md)

### Custom Responses
- [JSONResponse](./json-response.md)
- [RedirectResponse](./redirect-response.md)

### WebSockets
- [WebSocket Intro](./websockets-intro.md)
- [Connection Manager](./websockets-managing-connections.md)
- [Broadcasting](./websockets-broadcast.md)

### Security
- [OAuth2 Password](./security-oauth2-password.md)
- [JWT](./security-jwt.md)
- [API Key](./security-api-key.md)
- [OAuth2 Scopes](./security-scopes.md)

### LLM Integration
- [Evaluation Endpoint](./llm-evaluation-endpoint.md)
- [Streaming Endpoint](./llm-streaming-endpoint.md)

### FastMCP Integration
- [FastMCP Events](./integration-fastmcp-events.md)
- [FastMCP Shared Middleware](./integration-fastmcp-middleware.md)

### Configuration
- [Pydantic Settings](./configuration-pydantic-settings.md)
- [Environment Files](./configuration-environment.md)

### Logging & Operations
- [Logging Configuration](./logging.md)

### Deployment
- [Uvicorn Workers](./deployment-uvicorn.md)
- [Gunicorn with Uvicorn](./deployment-gunicorn.md)
- [Docker](./deployment-docker.md)
- [Nginx Reverse Proxy](./deployment-nginx.md)

### Performance
- [Async Paths](./performance-async-paths.md)
- [Database Pooling](./performance-database-pool.md)
- [Response Compression](./performance-response-compression.md)

### Reference
- [Troubleshooting](./troubleshooting.md)
- [overview.md](./overview.md) — Topic hub and index

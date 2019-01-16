# AI for Earth Hosted Acceptance Criteria
AI for Earth Grantees have the option of hosting their completed APIs on the official AI for Earth API platform.  These APIs are subject to the AI for Earth acceptance criteria.  Each of the following sections identify a requirement that must be met before the API is migrated to the AI for Earth hosting platform.

## API Design

### Input validation
Validation of API input must be performed prior to any processing.  This ensures fail-fast, decreases unnecessary resource utilization, and provides immediate information to the caller.

### Fast response
For long-running/async APIs, a task id must be immediately returned to the caller.  Ensure that threading or parallel processing is utilized.

For synchronous APIs, a result must be returned in fewer than 5 seconds.  If not, the API shall be converted to an async API and must utilize the task manager.

### Stateless or distributed state
All APIs must maintain a stateless design among requests.  If state is required between requests, a distributed state system must be implemented.  This state system must be atomic and lock-free in nature and must be able to handle loads associated with the API.

## Testing
APIs are to be tested in the following categories and, when applicable, results submitted with the request for acceptance.

### Functional
- Test functionality against requirements and API design specification
- Test typical use cases
- Test edge cases, including any possible out-of-bounds input
- Test very large inputs and very small inputs
- Test empty input

### Bad requests
- Test unsupported REST methods
- Test bad input
- Test permission issues for SAS Blobs, etc.

### Performance
- Test for timeouts when handling large inputs
- Gather metrics relating to running on GPU vs CPU
- Ensure that all failure points occur early in execution (fail-fast)
- Tune based on performance testing

### Load
- Gather metrics for incremental loads
- Identify maximum load for a single instance

## Documentation
Several areas of the API require documentation.  The documentation must be versioned with the API.

### Functional
- Document the purpose, use cases, and end-to-end scenarios
- Document relationship between input and output
- Document typical usage and edge case usage

### API Swagger
- The API must be Swagger documented, which includes input, output, schemas, etc.
- Swagger documentation must include sample inputs.

### Example input
- If the API requires input other than JSON, example input (files, etc.) must be provided.
- Example input must cover all computation possibilities.

### Usage instructions
Step-by-step usage instructions must be provided, which shall include:
- How to generate input data
- How to utilize output
- How to interpret statuses
- How to interpret error conditions
- How to fix errors

#### Integration
Document all integration points with external sources:
- How to generate input with external tools, software, etc.
- How to utilize output with external tools, software, etc.
- How to utilize other APIs or software to create end-to-end capabilities

## Kubernetes
We host APIs in a custom Kubernetes cluster.  To ensure API availability and dynamic scaling, information needs to be provided for the following criteria.

### Resource consumption targets
- Typical CPU usage for a single request
- Maximum CPU usage for a single request
- GPU execution time
- CPU execution time
- Typical memory usage for a single request
- Maximum memory usage for a single request

### Docker reports health status
- The API must contain an endpoint that returns a health check.  This health check must be added to the Dockerfile, such as:
```Dockerfile
HEALTHCHECK --interval=1m --timeout=3s --start-period=20s \
    CMD curl -f http://localhost/ || exit 1
```

### Scaling targets
Based on the load of a single request (typical and largest), estimate the resource thresholds that indicate that the service must be scaled up and down.

## Reliability

### Non-recycling
A best effort shall be made to prevent an instance from continuous recycling.

### Fast recovery
Stagger the loading of large objects into memory such that an instance can quickly respond to requests upon startup.

## Devops
Since AI for Earth will be assuming initial DevOps, detailed instructions shall be provided for the following categories.

### Debugging instructions
Document all known possible failure cases and how to resolve them.  Document in the form of a playbook, where the case is identified and step-by-step directions, with code is provided.

### Test sample data
Provide several datasets that can be used for acceptance testing, load testing, stress testing, and functional testing.

### Setup/deployment instructions/requirements
Any custom setup instructions, along with required architectural components, must be clearly documented.

### Contact information (devops)
Provide, at least, three contacts for additional DevOps support.  This shall include a phone number, Email address, Slack/Teams channel, etc.

## Usage permissions
Clearly identify any restrictions for API usage.  This includes denoting any sensitive issues.

### API key distribution requirements
The following questions shall be answered:
- What restrictions exist for API usage?
- Who makes decisions on key approvals?  Provide contact information.

## Telemetry
AI for Earth collects telemetry from our back-end system in order to provide a reliable service.  No PII (personally identifiable information) is collected by AI for Earth.

### State/heartbeat reporting
The API shall include an endpoint that reports the state of the service.

### Performance
Performance metrics, along with trace logging, must be included.  The trace logging shall include execution time.  To aid in performance requirement identification, input size, etc. should be included with the trace log.

### External sink
Telemetry is collected by AI for Earth for our back-end system.  Additional logging can be sent to the API owner's Application Insights instance.  Provide this information so that logs can be distributed.

### No PII
Absolutely no PII (personally identifiable information) shall be collected by the API.

### Alerting
Identify alert conditions based on the collected telemetry.  Include the response to such alerts in the DevOps playbook.
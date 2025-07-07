# Phase 15: Architectural Redesign - Implementation Plan

## Overview
This phase transitions from tool execution architecture to a simplified streaming approach where tools and data sources are configuration parameters that modify LLM behavior via system prompts. The work is divided into 7 sequential sub-parts, each with clear deliverables and success criteria.

For testing, use  `uv run pytest -v tests --timeout=10`


---

## Part 1: Test-Driven Development Setup
**Objective**: Create comprehensive failing tests that define the new architecture behavior

This part focuses on writing tests that will initially fail but define exactly how the new system should behave. The tests will serve as the specification for the new architecture, covering tool selection as configuration parameters, system prompt modification, single streaming responses, and Alpine.js integration points. These tests should be detailed enough that a developer can implement the new architecture purely by making the tests pass.

The key challenge here is writing tests that fail for the right reasons - they should fail because the current implementation executes tools instead of treating them as configuration, and because the current system uses dual LLM calls instead of single streaming responses. The tests should also define the expected Alpine.js integration points and API contracts for the frontend.

**Success Criteria**:
- [x] 8-10 new failing tests written in `test_phase_15_architecture.py`
- [x] Tests cover tool selection as configuration (not execution)
- [x] Tests verify system prompt modification based on tool selection
- [x] Tests ensure single streaming response pattern for all interactions
- [x] Tests define Alpine.js integration contracts
- [x] All new tests fail initially due to current tool execution logic
---

## Part 2: Backend Tool Execution Removal
**Objective**: Remove all tool execution logic and implement system prompt modification

This part involves surgically removing the tool execution logic from the chat router while preserving the session management, WebSocket communication, and streaming response functionality. The focus is on replacing the dual LLM call pattern (tool detection + streaming) with a single streaming call that incorporates tool information via system prompt modification. This requires careful refactoring to ensure that tool selections are captured and processed as configuration parameters rather than executable functions.

The implementation should maintain backward compatibility for all non-tool functionality while completely changing how tools are handled. Tool selections should be logged and potentially streamed to the frontend for user feedback, but no actual tool execution should occur. The system prompt should be dynamically modified to include relevant tool capabilities based on user selections.

**Success Criteria**:
- [x] Tool execution logic removed from `/app/app/routers/chat.py` (lines 149-204)
- [x] Dual LLM call pattern replaced with single streaming call
- [x] System prompt modification implemented based on tool selection
- [x] Tool selections logged and streamed to frontend ("tool:selected calculator")
- [x] All existing streaming functionality preserved
- [x] Session management unchanged
- [x] WebSocket communication maintained
- [x] Calculator tool demo system prompt includes mathematical capabilities

---

## Part 3: API Contract Updates
**Objective**: Update API endpoints to accept and process tool/data source selections as parameters

This part focuses on updating the chat API endpoints to accept the new parameter structure while maintaining backward compatibility. The API should accept `selected_tools`, `selected_data_sources`, and `llm_name` as additional parameters alongside the message content. These parameters should be processed and stored in the session state, used for system prompt modification, and potentially logged for debugging and user feedback.

The API changes should be minimal and non-breaking, with optional parameters that default to empty arrays or null values. The endpoint should validate the incoming parameters and provide clear error messages for invalid tool or data source selections. The response format should remain the same streaming format, but may include additional metadata about tool selections in the stream.

**Success Criteria**:
- [x] Chat API accepts `selected_tools` array parameter
- [x] Chat API accepts `selected_data_sources` array parameter  
- [x] Chat API accepts `llm_name` parameter
- [x] Parameters stored in session state
- [x] Backward compatibility maintained (parameters optional)
- [x] Parameter validation with clear error messages
- [x] Tool selections included in session logging

---

## Part 4: System Prompt Engine Implementation
**Objective**: Create dynamic system prompt generation based on tool and data source selections

This part involves building a flexible system prompt engine that can dynamically modify the LLM's system prompt based on user selections. The engine should have a base system prompt and then append relevant sections for each selected tool or data source. For the calculator tool demo, this means adding specific instructions about mathematical capabilities and encouraging the LLM to use calculation language.

The system prompt engine should be modular and extensible, allowing for easy addition of new tools and data sources in the future. It should also support different prompt templates for different LLM providers if needed. The engine should be well-tested and include logging of the final system prompts for debugging purposes.

**Success Criteria**:
- [x] Base system prompt loader from `system_prompt.md`
- [x] Dynamic prompt modification for calculator tool selection
- [x] Modular prompt sections for different tools
- [x] Data source context integration in system prompts
- [x] System prompt logging for debugging
- [x] Support for multiple tool combinations
- [x] Extensible architecture for future tools
- [x] LLM provider-specific prompt templates (if needed)

---

## Part 5: Alpine.js Frontend Integration
**Objective**: Implement complete npm-based frontend with Alpine.js reactive components

This part implements a modern npm-based frontend using Vite as the build system and Alpine.js for reactive components. The implementation includes a complete restructure from static files to a proper frontend development environment with hot reloading, dependency management, and optimized builds.

**Key Implementation Details**:
- **Build System**: Vite configuration with proxy to FastAPI backend (port 8000)
- **Alpine.js v3.x**: CDN integration for lightweight reactivity without build complexity
- **Styling**: Tailwind CSS via CDN for rapid development and consistent dark theme
- **State Management**: Comprehensive Alpine.js component with reactive data binding
- **WebSocket Integration**: Real-time status updates and tool selection feedback
- **Streaming Responses**: Fetch API with ReadableStream for real-time chat updates

**Frontend Structure**:
```
frontend/
├── package.json          # npm dependencies (alpinejs, vite)
├── vite.config.js        # Vite config with proxy to backend
├── index.html           # Main HTML with Alpine.js CDN
├── src/
│   ├── main.js          # Alpine.js component and initialization
│   └── styles/main.css  # Tailwind CSS and custom styles
└── dist/                # Built assets served by FastAPI
```

**Success Criteria**:
- [x] Complete npm project structure with Vite build system
- [x] Alpine.js v3.x integration via CDN in index.html
- [x] Main container uses `x-data="chatApp()"` with comprehensive state
- [x] Reactive state: `selectedModel`, `selectedTools`, `selectedDataSources`, `messages`
- [x] Multi-select dropdowns with `x-model` bindings for tools and data sources
- [x] API integration for fetching available LLM models dynamically
- [x] Streaming response handling with real-time message updates
- [x] WebSocket connection for status updates and tool feedback
- [x] Tailwind CSS styling with dark theme and responsive design
- [x] Automatic DOM updates without manual manipulation

---

## Part 6: Streaming Response Integration
**Objective**: Implement single streaming pattern with tool selection feedback

This part focuses on perfecting the streaming response pattern to work seamlessly with the new architecture. The implementation should handle the single streaming LLM call while providing feedback about tool selections and maintaining real-time updates. The streaming should include metadata about tool selections when relevant and provide clear user feedback about what capabilities are available.

The streaming implementation should be robust and handle various edge cases like connection interruptions, large responses, and rapid successive messages. It should also integrate cleanly with the Alpine.js reactive components to provide smooth UI updates. The implementation should include proper error handling and user feedback for failed streams or API issues.

**Success Criteria**:
- [x] Single streaming pattern implemented for all interactions
- [x] Tool selection feedback integrated into stream
- [x] Alpine.js reactive updates during streaming
- [x] Error handling for stream interruptions
- [x] Metadata streaming for tool selections
- [x] Real-time UI updates without flickering
- [x] Robust handling of large responses
- [x] Clear user feedback for tool availability

---

## Part 7: Test Suite Alignment and Validation
**Objective**: Fix existing tests and ensure comprehensive coverage of new architecture

This part involves updating the existing test suite to align with the new architecture while ensuring that all new functionality is properly tested. The focus is on fixing the tests that currently expect tool execution and updating them to verify the new streaming-only behavior. This includes updating `test_chat.py` and `test_container_integration.py` to remove dual LLM call expectations and tool execution assertions.

The updated test suite should provide comprehensive coverage of the new architecture, including system prompt modification, tool selection processing, Alpine.js integration points, and streaming behavior. All tests should pass consistently, and the suite should serve as documentation for how the new system works. The implementation should also include performance tests to ensure the new architecture doesn't introduce latency issues.

**Success Criteria**:
- [x] All tests from Part 1 now pass (via new integration tests)
- [x] `test_chat.py` updated to expect single streaming responses
- [x] `test_container_integration.py` aligned with new architecture
- [x] No tests expect tool execution behavior
- [x] Comprehensive coverage of system prompt modification
- [x] Alpine.js integration points tested
- [x] Performance tests for streaming responses
- [x] All test suites pass consistently (46 passing tests achieved)

---

## Implementation Guidelines

### Sequential Dependencies
Each part builds on the previous parts:
- Part 1 defines the target behavior through tests
- Part 2 removes the conflicting backend logic
- Part 3 updates the API contracts
- Part 4 implements the core system prompt engine
- Part 5 adds the frontend reactivity
- Part 6 perfects the streaming integration
- Part 7 validates everything works correctly

### Time Estimates
- **Part 1**: 2-3 hours (test design and implementation)
- **Part 2**: 3-4 hours (backend refactoring)
- **Part 3**: 1-2 hours (API updates)
- **Part 4**: 2-3 hours (system prompt engine)
- **Part 5**: 3-4 hours (complete frontend restructure with npm/Vite/Alpine.js)
- **Part 6**: 2-3 hours (streaming implementation)
- **Part 7**: 1-2 hours (test fixes and validation)

**Total Estimated Time**: 14-21 hours

### Quality Gates
Each part should be completed and tested before moving to the next part. The tests from Part 1 serve as the acceptance criteria for the entire phase - when all tests pass, the architectural redesign is complete.
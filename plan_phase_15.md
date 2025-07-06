# Phase 15: Architectural Redesign - Implementation Plan

## Overview
This phase transitions from tool execution architecture to a simplified streaming approach where tools and data sources are configuration parameters that modify LLM behavior via system prompts. The work is divided into 7 sequential sub-parts, each with clear deliverables and success criteria.

For testing, use  `uv run pytest -v tests --timeout=20`


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
**Objective**: Implement reactive frontend components with Alpine.js for clean state management

This part focuses on integrating Alpine.js to create a reactive frontend that can cleanly manage the selection of tools, data sources, and models. The implementation should use Alpine.js directives like `x-data`, `x-model`, and `@change` to create a reactive component that automatically updates the UI when selections change. The component should handle the API calls for fetching available models and managing the chat state.

The Alpine.js integration should be implemented incrementally, starting with the main chat container and then adding reactive behavior to dropdowns and selection components. The implementation should maintain the existing WebSocket functionality while adding clean state management for the new configuration parameters. The component should handle streaming responses elegantly and provide feedback when tools are selected.

**Success Criteria**:
- [ ] Main container uses `x-data="chatApp()"` directive
- [ ] Reactive state management for `selectedModel`, `selectedTools`, `selectedDataSources`
- [ ] Dropdown components with `x-model` bindings
- [ ] API integration for fetching available models
- [ ] Streaming response handling with Alpine reactivity
- [ ] Tool selection feedback in UI
- [ ] Automatic DOM updates without manual manipulation
- [ ] Clean separation between configuration and execution in UI

---

## Part 6: Streaming Response Integration
**Objective**: Implement single streaming pattern with tool selection feedback

This part focuses on perfecting the streaming response pattern to work seamlessly with the new architecture. The implementation should handle the single streaming LLM call while providing feedback about tool selections and maintaining real-time updates. The streaming should include metadata about tool selections when relevant and provide clear user feedback about what capabilities are available.

The streaming implementation should be robust and handle various edge cases like connection interruptions, large responses, and rapid successive messages. It should also integrate cleanly with the Alpine.js reactive components to provide smooth UI updates. The implementation should include proper error handling and user feedback for failed streams or API issues.

**Success Criteria**:
- [ ] Single streaming pattern implemented for all interactions
- [ ] Tool selection feedback integrated into stream
- [ ] Alpine.js reactive updates during streaming
- [ ] Error handling for stream interruptions
- [ ] Metadata streaming for tool selections
- [ ] Real-time UI updates without flickering
- [ ] Robust handling of large responses
- [ ] Clear user feedback for tool availability

---

## Part 7: Test Suite Alignment and Validation
**Objective**: Fix existing tests and ensure comprehensive coverage of new architecture

This part involves updating the existing test suite to align with the new architecture while ensuring that all new functionality is properly tested. The focus is on fixing the tests that currently expect tool execution and updating them to verify the new streaming-only behavior. This includes updating `test_chat.py` and `test_container_integration.py` to remove dual LLM call expectations and tool execution assertions.

The updated test suite should provide comprehensive coverage of the new architecture, including system prompt modification, tool selection processing, Alpine.js integration points, and streaming behavior. All tests should pass consistently, and the suite should serve as documentation for how the new system works. The implementation should also include performance tests to ensure the new architecture doesn't introduce latency issues.

**Success Criteria**:
- [ ] All tests from Part 1 now pass
- [ ] `test_chat.py` updated to expect single streaming responses
- [ ] `test_container_integration.py` aligned with new architecture
- [ ] No tests expect tool execution behavior
- [ ] Comprehensive coverage of system prompt modification
- [ ] Alpine.js integration points tested
- [ ] Performance tests for streaming responses
- [ ] All test suites pass consistently (target: 60+ passing tests)

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
- **Part 5**: 2-3 hours (Alpine.js integration)
- **Part 6**: 2-3 hours (streaming implementation)
- **Part 7**: 1-2 hours (test fixes and validation)

**Total Estimated Time**: 13-20 hours

### Quality Gates
Each part should be completed and tested before moving to the next part. The tests from Part 1 serve as the acceptance criteria for the entire phase - when all tests pass, the architectural redesign is complete.
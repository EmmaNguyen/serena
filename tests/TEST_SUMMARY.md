# Test Summary for Serena

## API Tests (test_api.py) — 39 tests

| Test Class | Test Method | What it covers |
|------------|-------------|----------------|
| TestChatFunction | test_chat_basic_call | Basic chat API call |
| TestChatFunction | test_chat_with_system_prompt | Chat with system prompt |
| TestChatFunction | test_chat_max_tokens | Custom max_tokens parameter |
| TestMemoryAgent | test_get_context | Context retrieval structure |
| TestMemoryAgent | test_update_simple_key | Update with simple key |
| TestMemoryAgent | test_update_nested_key | Update with nested dot notation |
| TestMemoryAgent | test_log_mood | Mood logging functionality |
| TestMemoryAgent | test_mood_trend | Mood trend calculation |
| TestMemoryAgent | test_save_journal_entry | Journal entry saving |
| TestMindfulnessAgent | test_guide_breathing_box | Box breathing guide |
| TestMindfulnessAgent | test_guide_breathing_478 | 4-7-8 breathing guide |
| TestMindfulnessAgent | test_guide_breathing_default | Default breathing style |
| TestMindfulnessAgent | test_respond | respond() method |
| TestJournalingAgent | test_parse_insights_valid | Parsing valid INSIGHTS JSON |
| TestJournalingAgent | test_parse_insights_none | Parsing when no INSIGHTS tag present |
| TestJournalingAgent | test_parse_insights_invalid_json | Parsing invalid JSON |
| TestJournalingAgent | test_clean_response | Stripping INSIGHTS tags from response |
| TestJournalingAgent | test_generate_prompt | Prompt generation |
| TestHabitCoachAgent | test_check_in | Habit check-in |
| TestHabitCoachAgent | test_mark_complete_full | Mark habit as fully complete |
| TestHabitCoachAgent | test_mark_complete_partial | Mark habit as partial |
| TestHabitCoachAgent | test_mark_complete_best_streak | best_streak updates when new streak exceeds it |
| TestHabitCoachAgent | test_mark_complete_best_streak_no_update_at_equal | best_streak unchanged when equal to current |
| TestHabitCoachAgent | test_respond | respond() method |
| TestOrchestratorAgent | test_classify_mindfulness | Classify mindfulness intent |
| TestOrchestratorAgent | test_classify_journaling | Classify journaling intent |
| TestOrchestratorAgent | test_classify_invalid_json | Classify with invalid JSON |
| TestOrchestratorAgent | test_route_mindfulness | Route to mindfulness agent |
| TestOrchestratorAgent | test_route_journaling | Route to journaling agent |
| TestOrchestratorAgent | test_route_meta | Route to meta (default) agent |
| TestOrchestratorAgent | test_history_truncation | History truncation to 20 messages |
| TestAzureSearchMemory | test_upsert | Upsert operation |
| TestAzureSearchMemory | test_search | Search operation |
| TestAzureSearchMemory | test_search_empty | Search with no results |
| TestAzureBlobJournal | test_save_entry | Saving journal entry |
| TestAzureBlobJournal | test_load_entry | Loading journal entry (stub) |
| TestAzureLanguagePipeline | test_analyze_with_fallback | Analysis with GPT fallback |
| TestAzureLanguagePipeline | test_analyze_invalid_json | Analysis with invalid JSON |
| TestAzureLanguagePipeline | test_compute_habit_mood_correlation | Habit-mood correlation computation |

## Security Tests (test_security.py) — 46 tests

| Test Class | Test Method | What it covers |
|------------|-------------|----------------|
| TestJSONInjection | test_parse_insights_malicious_json | Malicious JSON payloads in parse_insights() |
| TestJSONInjection | test_parse_insights_invalid_json | Invalid JSON in parse_insights() |
| TestJSONInjection | test_parse_insights_missing_closing_tag | Incomplete INSIGHTS tags |
| TestJSONInjection | test_parse_insights_xss_attempt | XSS attempts in JSON responses |
| TestMemoryInjection | test_update_prototype_pollution | Prototype pollution via update() |
| TestMemoryInjection | test_update_constructor_pollution | Constructor pollution via update() |
| TestMemoryInjection | test_update_deep_nested_key | Deeply nested keys |
| TestMemoryInjection | test_update_special_characters | Special characters in keys |
| TestMemoryInjection | test_update_overwrite_critical_fields | Overwriting critical fields |
| TestInputSanitization | test_log_mood_extreme_values | Extreme mood score values |
| TestInputSanitization | test_save_journal_entry_null_bytes | Null bytes in journal entries |
| TestInputSanitization | test_save_journal_entry_extremely_long | Extremely long input |
| TestInputSanitization | test_user_id_injection | User ID validation / path traversal |
| TestAPIKeySecurity | test_missing_api_key | Behavior when API keys are absent |
| TestAPIKeySecurity | test_api_key_not_logged | API keys not written to logs |
| TestAPIKeySecurity | test_max_calls_enforcement | MAX_CALLS budget limit triggers RuntimeError |
| TestOrchestratorSecurity | test_classify_json_injection | Malicious JSON in classify() |
| TestOrchestratorSecurity | test_classify_invalid_json | Invalid JSON in classify() |
| TestOrchestratorSecurity | test_route_history_bounded | History truncation prevents unbounded growth |
| TestAzureLanguagePipelineSecurity | test_analyze_malicious_input | Malicious text in analyze() |
| TestAzureLanguagePipelineSecurity | test_analyze_json_injection | JSON injection in analyze() |
| TestAzureBlobJournalSecurity | test_save_entry_path_traversal | Path traversal prevention in blob names |
| TestAzureBlobJournalSecurity | test_save_entry_special_chars | Special characters in user IDs |
| TestAzureSearchMemorySecurity | test_upsert_injection | Content injection in upsert() |
| TestAzureSearchMemorySecurity | test_search_injection | Query sanitization in search() |
| TestCleanResponse | test_clean_response_xss | XSS removal in clean_response() |
| TestCleanResponse | test_clean_response_multiple_tags | Multiple INSIGHTS tags stripped |
| TestBudgetGuard | test_budget_guard_raises_when_limit_exceeded | RuntimeError raised at MAX_CALLS |
| TestBudgetGuard | test_budget_guard_allows_call_at_limit_minus_one | Call at MAX_CALLS - 1 succeeds |
| TestHabitCoachSecurity | test_mark_complete_injection_slug_does_not_crash | Injection slug does not crash |
| TestHabitCoachSecurity | test_mark_complete_unknown_slug_silently_creates_entry | Unknown slug creates arbitrary entry |
| TestInputTypeSafety | test_log_mood_non_numeric_score_corrupts_mood_trend | Non-numeric score corrupts trend |
| TestInputTypeSafety | test_log_mood_none_score_corrupts_mood_trend | None score corrupts trend |
| TestInputTypeSafety | test_update_empty_key_creates_empty_string_entry | Empty key creates empty-string entry |
| TestInputTypeSafety | test_update_double_dot_key_creates_empty_segment | Double-dot key creates empty segment |
| TestParseInsightsEdgeCases | test_parse_insights_empty_block_returns_none | Empty INSIGHTS block returns None |
| TestParseInsightsEdgeCases | test_parse_insights_whitespace_only_returns_none | Whitespace-only block returns None |
| TestParseInsightsEdgeCases | test_parse_insights_json_array_returns_non_dict | JSON array (not object) handled |
| TestParseInsightsEdgeCases | test_parse_insights_deeply_nested_json_does_not_crash | Deep nesting does not crash |
| TestRiskFlagSafety | test_risk_flag_absent_from_response_defaults_to_falsy | Absent risk_flag defaults falsy |
| TestRiskFlagSafety | test_risk_flag_true_is_returned_but_not_escalated | risk_flag=True not escalated to crisis response |
| TestPromptInjection | test_classify_with_system_override_attempt | System-role override attempt in user message |
| TestPromptInjection | test_route_with_empty_string_does_not_crash | Empty string routed without crash |
| TestPromptInjection | test_synthesise_embeds_raw_user_message_unescaped | Raw user message embedded unescaped |
| TestBlobJournalEdgeCases | test_save_entry_empty_user_id_creates_malformed_path | Empty user_id creates malformed blob path |
| TestBlobJournalEdgeCases | test_save_entry_empty_content_does_not_crash | Empty content does not crash |

## API Handler Tests (test_api_handler.js) — 16 tests

| Test | What it covers |
|------|----------------|
| missing messages field returns 400 | Rejects requests with no messages key |
| null messages returns 400 | Rejects null messages value |
| string messages returns 400 | Rejects non-array messages |
| object messages (not array) returns 400 | Rejects object instead of array |
| null body is treated as empty — returns 400 | Handles null request body gracefully |
| missing env vars returns 503 | 503 when both endpoint and key absent |
| missing API key alone returns 503 | 503 when only key is absent |
| maxTokens above 2000 is clamped to 2000 | Upper bound enforced |
| maxTokens below 1 is clamped to 1 | Lower bound enforced |
| absent maxTokens defaults to 300 | Default value applied |
| non-numeric maxTokens ("abc") defaults to 300 | Bad string falls back to default |
| null maxTokens defaults to 300 | Null falls back to default |
| messages array with 30 entries is truncated to last 20 | Context window guard |
| messages array with exactly 20 entries is not truncated | Boundary: 20 is not truncated |
| API key is not included in the response body | Key never echoed to client |
| API key is sent in request header not body | Key sent as api-key header only |

## JavaScript Security Tests (test_js_security.html) — 10 tests

| Test | What it covers |
|------|----------------|
| innerHTML XSS | Scripts inserted via innerHTML are present in DOM |
| localStorage API Key Storage | API keys in localStorage are accessible to any script |
| localStorage Key XSS | Malicious key names storable in localStorage |
| Input Sanitization | User input stored without sanitization |
| JSON.parse Prototype Pollution | JSON.parse cannot pollute prototype |
| eval() Usage | No direct eval() usage in code |
| Content Security Policy | CSP header configured via staticwebapp.config.json |
| Event Handler XSS | Event handlers injectable via innerHTML |
| URL Parameter Injection | URL parameters not validated |
| localStorage Quota | Quota limit enforced (DoS prevention) |

## Summary

| File | Type | Tests |
|------|------|-------|
| `test_api.py` | Python unit | 39 |
| `test_security.py` | Python security | 46 |
| `test_api_handler.js` | Node.js | 16 |
| `test_js_security.html` | Browser JS | 10 |
| **Total** | | **111** |

### Running all tests

```bash
# All Python tests (85 total)
python -m pytest tests/ -v

# Node.js API handler tests (16 total)
node --test tests/test_api_handler.js

# Browser JS tests — open in browser
# tests/test_js_security.html
```

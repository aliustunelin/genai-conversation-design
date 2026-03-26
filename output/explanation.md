# Assessment Deliverable — Written Note

## Logic Behind the Task

The conversation is structured around a **coding task with escalating complexity**:
a progression from basic string parsing to a full regex engine implementation.

Each turn builds on the concepts from the previous one (bracket matching → expression parsing → pattern matching),
creating a natural escalation that tests the model's ability to handle increasingly complex implementations.

## Why Earlier Turns Were Expected to Succeed

### Turn 1: Balanced Parentheses Checker
- This is a classic, well-known problem with a straightforward stack-based solution.
- GPT-4o has been trained on thousands of examples of this exact problem.
- The prompt is clear, structured, and asks for a well-scoped deliverable.

### Turn 2: Mathematical Expression Evaluator
- The Shunting-Yard algorithm is a well-documented algorithm found in many textbooks and online resources.
- While more complex, it is still a single, well-defined algorithm with clear rules.
- The prompt explicitly names the algorithm, giving the model a clear direction.
- GPT-4o handles algorithmic implementation well when the algorithm is well-known.

## What Changed in the Final Turn

Turn 3 asks for a **complete regex engine from scratch** supporting 14 distinct features simultaneously:
literal matching, wildcards, quantifiers (greedy and non-greedy), alternation, grouping,
character classes, shorthand classes, anchors, escape sequences, lookahead, and lookbehind.

The critical differences from previous turns:
1. **Combinatorial complexity:** Each feature is individually implementable, but their *interactions* create exponential edge cases.
2. **Non-greedy matching in full-string context:** Lazy quantifiers behave differently when the engine must match the *entire* string vs. finding a substring match.
3. **Variable-length lookbehind:** This is famously difficult — even production regex engines (like Python's `re`) restrict lookbehind to fixed-length patterns. The prompt explicitly asks for variable-length lookbehind support.
4. **20 verifiable test cases:** Forces the model to produce code that must pass every case simultaneously, rather than generating plausible-looking code.

## What Limitations of the Model Were Exposed

1. **Integration complexity ceiling:** GPT-4o can implement individual regex features correctly, but combining 14+ features into a single coherent engine exceeds its ability to maintain consistency across all interactions.

2. **Algorithmic depth:** Building a correct NFA/backtracking engine that handles both greedy and non-greedy quantifiers with lookaround assertions requires deep algorithmic reasoning that the model approximates but cannot execute flawlessly in a single generation.

3. **Edge case reasoning:** The model struggles with cases where features interact unexpectedly — e.g., nested groups with quantifiers inside alternation (`((a|b)*c)+`), or negative lookbehind combined with character classes.

4. **Self-verification gap:** Despite being asked to test against specific cases, the model cannot actually execute its own code to verify correctness. It generates test assertions based on what the code *should* do, not what it *actually* does — leading to false confidence in the output.

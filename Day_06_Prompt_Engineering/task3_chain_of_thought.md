# Task 3: Applying Chain-of-Thought (CoT) Prompting

## Introduction

Large Language Models (LLMs) often produce the correct answer directly, but they do not always explain how they reached that answer. For tasks involving calculations, logical reasoning, or multiple decision steps, understanding the reasoning process is just as important as obtaining the final answer.

Chain-of-Thought (CoT) prompting is a simple technique that encourages the model to think through a problem before answering. A common way to apply this technique is by adding the instruction:

> **"Let's think step by step."**

In this task, I compared the model's responses with and without Chain-of-Thought prompting on three different reasoning problems.

---

# Experiment 1: Mathematical Reasoning

### Problem

```text
A shop sells a notebook for $12.
Sarah buys 5 notebooks and pays with $100.
How much change should she receive?
```

---

## Prompt Without CoT

```text
A shop sells a notebook for $12.
Sarah buys 5 notebooks and pays with $100.

How much change should she receive?
```

### Model Response

```text
$40
```

The model returned the correct answer immediately. While the result is accurate, no explanation is provided, making it difficult to verify the calculation.

---

## Prompt With CoT

```text
Let's think step by step.

A shop sells a notebook for $12.
Sarah buys 5 notebooks and pays with $100.

How much change should she receive?
```

### Model Response

```text
Each notebook costs $12.

Cost of 5 notebooks = 5 × 12 = $60.

Sarah paid $100.

Change = $100 − $60 = $40.

Final Answer: $40
```

With the Chain-of-Thought prompt, the model explains every calculation before giving the final answer. The response is much easier to follow and verify.

---

# Experiment 2: Logical Reasoning

### Problem

```text
Ali is older than Ahmed.
Ahmed is older than Bilal.

Who is the oldest?
```

---

## Prompt Without CoT

```text
Ali is older than Ahmed.
Ahmed is older than Bilal.

Who is the oldest?
```

### Model Response

```text
Ali
```

The answer is correct, but the reasoning behind the conclusion is not shown.

---

## Prompt With CoT

```text
Let's think step by step.

Ali is older than Ahmed.
Ahmed is older than Bilal.

Who is the oldest?
```

### Model Response

```text
Ali is older than Ahmed.

Ahmed is older than Bilal.

This means Ali is also older than Bilal.

Therefore, Ali is the oldest.

Final Answer: Ali
```

In this case, the model clearly explains the logical relationship before reaching the conclusion, making the answer more transparent.

---

# Experiment 3: Multi-Step Arithmetic

### Problem

```text
A train travels at 60 km/h for 2.5 hours.

How far does it travel?
```

---

## Prompt Without CoT

```text
A train travels at 60 km/h for 2.5 hours.

How far does it travel?
```

### Model Response

```text
150 km
```

The response is correct but does not explain how the distance was calculated.

---

## Prompt With CoT

```text
Let's think step by step.

A train travels at 60 km/h for 2.5 hours.

How far does it travel?
```

### Model Response

```text
Distance is calculated using the formula:

Distance = Speed × Time

Distance = 60 × 2.5

Distance = 150 km

Final Answer: 150 km
```

Adding the Chain-of-Thought instruction resulted in a more detailed and understandable solution.

---

# Comparison

| Aspect | Without CoT | With CoT |
|---------|-------------|----------|
| Final answer | Usually correct | Correct |
| Explanation | Minimal or none | Clear step-by-step reasoning |
| Transparency | Low | High |
| Easy to verify | No | Yes |
| Best suited for | Simple questions | Multi-step reasoning problems |

---

# Discussion

Across all three experiments, both prompts produced the correct final answers. However, adding the phrase **"Let's think step by step."** consistently encouraged the model to explain its reasoning before presenting the solution.

This additional reasoning makes it easier to understand how the answer was obtained and allows users to verify each intermediate step. Although the final answer remained the same in these examples, the overall quality and clarity of the response improved noticeably.

---

# Conclusion

This experiment demonstrates that Chain-of-Thought prompting is a simple but effective technique for improving reasoning-based responses from Large Language Models. While direct prompting is often sufficient for straightforward questions, CoT prompting produces more transparent and informative answers, making it especially useful for mathematical calculations, logical reasoning, and other multi-step problems.
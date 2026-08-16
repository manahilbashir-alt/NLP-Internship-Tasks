# Temperature, Top-P, and Max Tokens Experiment


## Prompt

Write a short motivational message for computer science students.


## Experiment Results


| Experiment | Temperature | Top-P | Max Tokens | Expected Behavior |
|---|---|---|---|---|
| Low Creativity | 0.2 | 0.5 | 50 | More predictable and focused output |
| Balanced | 0.7 | 0.9 | 100 | Balance between creativity and accuracy |
| High Creativity | 1.2 | 1.0 | 150 | More diverse and creative responses |


## Parameter Explanation


### Temperature

Controls randomness in generated responses.

- Low temperature → More consistent answers
- High temperature → More creative answers


### Top-P

Controls how many possible tokens are considered.

- Lower Top-P → More focused output
- Higher Top-P → More variety


### Max Tokens

Controls the maximum length of the generated response.


## Conclusion

Changing generation parameters directly affects the style and creativity of AI responses. Lower values produce focused answers, while higher values increase creativity and diversity.
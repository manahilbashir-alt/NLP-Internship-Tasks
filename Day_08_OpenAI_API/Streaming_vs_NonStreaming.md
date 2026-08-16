# Streaming vs Non-Streaming Responses

## Non-Streaming Response

In a normal API request, the complete response is generated first and then returned to the user.

### Advantages:
- Simple implementation
- Easier response handling

### Disadvantages:
- User waits until the entire response is generated


## Streaming Response

In streaming, the response is sent in small chunks as soon as they are generated.

### Advantages:
- Faster user experience
- Text appears gradually
- Useful for chatbots and assistants

### Disadvantages:
- Slightly more complex implementation


## Comparison

| Feature | Non-Streaming | Streaming |
|---|---|---|
| Response delivery | Complete response at once | Chunk by chunk |
| User experience | Waiting time before seeing output | Immediate visible output |
| Complexity | Simple | More complex |
| Best for | Short responses | Long responses and chat applications |
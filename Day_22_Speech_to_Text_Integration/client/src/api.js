const BASE_URL = 'http://localhost:8000'

export async function fetchSessions() {
  const res = await fetch(`${BASE_URL}/api/sessions`)
  if (!res.ok) throw new Error('Failed to load sessions')
  return res.json()
}

export async function fetchSession(sessionId) {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}`)
  if (!res.ok) throw new Error('Failed to load session')
  return res.json()
}

export async function deleteSession(sessionId) {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete session')
  return res.json()
}

export async function generateTitle(sessionId) {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/title`, { method: 'POST' })
  if (!res.ok) throw new Error('Failed to generate title')
  return res.json()
}

/**
 * Re-runs the last assistant turn in place (does NOT resend/duplicate the
 * user message). The backend drops its own last assistant message and
 * regenerates from the existing history.
 */
export async function regenerateChat(sessionId) {
  const res = await fetch(`${BASE_URL}/api/chat/regenerate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Regenerate failed' }))
    throw new Error(err.detail || 'Regenerate failed')
  }
  return res.json()
}

export async function sendChat({ sessionId, message, persona, temperature, useTools, jsonMode }) {
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      persona,
      temperature,
      use_tools: useTools,
      json_mode: jsonMode,
    }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

/** Runs one of the 4 production prompt templates against a piece of input text. */
export async function runProductionPrompt(promptType, input) {
  const endpoint = promptType === 'structured_json'
    ? `${BASE_URL}/api/prompts/structured-json`
    : `${BASE_URL}/api/prompts/${promptType}`
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Prompt run failed' }))
    throw new Error(err.detail || 'Prompt run failed')
  }
  return res.json()
}

/**
 * Streams a chat response via Server-Sent Events.
 * onDelta(text) is called for each token chunk.
 * onDone({session_id, usage, latency_ms}) is called at the end.
 */
export async function streamChat({ sessionId, message, persona, temperature }, onDelta, onDone, onError) {
  try {
    const res = await fetch(`${BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        message,
        persona,
        temperature,
        stream: true,
      }),
    })
    if (!res.ok || !res.body) throw new Error('Stream request failed')

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop()
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const payload = JSON.parse(line.slice(6))
        if (payload.error) {
          onError?.(payload.error)
        } else if (payload.delta) {
          onDelta(payload.delta)
        } else if (payload.done) {
          onDone(payload)
        }
      }
    }
  } catch (e) {
    onError?.(e.message)
  }
}
export async function transcribeAudio(audioBlob) {
  const formData = new FormData()

  formData.append(
    'file',
    audioBlob,
    'recording.webm'
  )

  const res = await fetch(`${BASE_URL}/api/transcribe`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({
      detail: 'Transcription failed',
    }))

    throw new Error(err.detail || 'Transcription failed')
  }

  return res.json()
}

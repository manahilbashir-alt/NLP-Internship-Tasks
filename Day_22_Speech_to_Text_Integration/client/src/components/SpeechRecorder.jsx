import { useRef, useState } from 'react'
import { transcribeAudio } from '../api'

export default function SpeechRecorder({ onTranscription }) {
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])

  const [recording, setRecording] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function startRecording() {
    setError('')

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      })

      chunksRef.current = []

      const recorder = new MediaRecorder(stream)

      mediaRecorderRef.current = recorder

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop())

        const audioBlob = new Blob(chunksRef.current, {
          type: 'audio/webm',
        })

        setLoading(true)

        try {
          const result = await transcribeAudio(audioBlob)

          if (result.text) {
            onTranscription(result.text)
          } else {
            setError('No speech was detected.')
          }
        } catch (err) {
          setError(err.message)
        } finally {
          setLoading(false)
        }
      }

      recorder.start()
      setRecording(true)
    } catch (err) {
      setError(
        'Microphone permission is required. Please allow microphone access.'
      )
    }
  }

  function stopRecording() {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop()
      setRecording(false)
    }
  }

  return (
    <div className="flex items-center gap-2">
      {!recording ? (
        <button
          type="button"
          onClick={startRecording}
          disabled={loading}
          className="shrink-0 border border-codex-border text-codex-muted hover:text-gold-leaf hover:border-gold-leaf/50 rounded-md px-3 py-2 text-sm transition-colors disabled:opacity-50"
        >
          {loading ? 'Transcribing...' : '🎤'}
        </button>
      ) : (
        <button
          type="button"
          onClick={stopRecording}
          className="shrink-0 bg-rubric-red/10 border border-rubric-red/40 text-rubric-red rounded-md px-3 py-2 text-sm"
        >
          ⏹ Stop
        </button>
      )}

      {error && (
        <span className="text-xs text-rubric-red">
          {error}
        </span>
      )}
    </div>
  )
}
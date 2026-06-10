import { AxiosError } from 'axios'

interface ApiErrorPayload {
  error?: {
    code?: string
    message?: string
    request_id?: string
    details?: unknown
  }
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof AxiosError) {
    const payload = error.response?.data as ApiErrorPayload | undefined
    return payload?.error?.message ?? error.message ?? fallback
  }

  if (error instanceof Error) {
    return error.message
  }

  return fallback
}

export function getApiRequestId(error: unknown): string | undefined {
  if (!(error instanceof AxiosError)) {
    return undefined
  }

  const payload = error.response?.data as ApiErrorPayload | undefined
  return payload?.error?.request_id
}

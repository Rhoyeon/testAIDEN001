/**
 * AIDEN WebSocket Client
 *
 * Manages a WebSocket connection to the backend event stream for a given project.
 * Features auto-reconnect with exponential backoff and a typed event listener pattern.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Connection lifecycle states. */
export type ConnectionState =
  | "connecting"
  | "connected"
  | "disconnected"
  | "error";

/** Server-to-client message shape (mirrors backend WSMessage schema). */
export interface WSMessage {
  type: string;
  event: string;
  project_id: string;
  timestamp: string;
  data?: unknown;
}

/** Client-to-server message shape. */
export interface WSClientMessage {
  action: "subscribe" | "unsubscribe" | "ping";
  channel?: string | null;
}

export type MessageCallback = (message: WSMessage) => void;
export type StateChangeCallback = (state: ConnectionState) => void;

// ---------------------------------------------------------------------------
// WebSocket Manager
// ---------------------------------------------------------------------------

export class WebSocketManager {
  // Configuration
  private readonly baseUrl: string;
  private projectId: string | null = null;

  // Connection
  private ws: WebSocket | null = null;
  private state: ConnectionState = "disconnected";

  // Reconnect
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectAttempt = 0;
  private readonly maxReconnectDelay = 8_000; // 8 seconds
  private readonly baseReconnectDelay = 1_000; // 1 second
  private shouldReconnect = false;

  // Ping / keep-alive
  private pingTimer: ReturnType<typeof setInterval> | null = null;
  private readonly pingInterval = 30_000; // 30 seconds

  // Listeners
  private messageListeners: Set<MessageCallback> = new Set();
  private stateListeners: Set<StateChangeCallback> = new Set();

  constructor(baseUrl?: string) {
    // Derive WS URL from the configured API base or window location
    if (baseUrl) {
      this.baseUrl = baseUrl;
    } else if (typeof window !== "undefined") {
      const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const apiBase = process.env.NEXT_PUBLIC_WS_BASE_URL;
      if (apiBase) {
        this.baseUrl = apiBase;
      } else {
        this.baseUrl = `${wsProtocol}//${window.location.host}/api/v1`;
      }
    } else {
      this.baseUrl = "ws://127.0.0.1:8000/api/v1";
    }
  }

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------

  /** Current connection state. */
  getState(): ConnectionState {
    return this.state;
  }

  /** The project ID currently subscribed to, or null. */
  getProjectId(): string | null {
    return this.projectId;
  }

  /**
   * Connect to the WebSocket endpoint for the given project.
   * If already connected to the same project, this is a no-op.
   * If connected to a different project, disconnects first.
   */
  connect(projectId: string): void {
    if (this.projectId === projectId && this.state === "connected") {
      return;
    }

    // Disconnect from any previous project
    if (this.ws) {
      this.disconnect();
    }

    this.projectId = projectId;
    this.shouldReconnect = true;
    this.reconnectAttempt = 0;
    this.createConnection();
  }

  /** Cleanly close the WebSocket connection and stop reconnecting. */
  disconnect(): void {
    this.shouldReconnect = false;
    this.clearTimers();

    if (this.ws) {
      // Avoid triggering onclose reconnect logic
      this.ws.onclose = null;
      this.ws.onerror = null;
      this.ws.onmessage = null;
      this.ws.onopen = null;
      this.ws.close();
      this.ws = null;
    }

    this.projectId = null;
    this.setState("disconnected");
  }

  /** Register a listener for incoming messages. Returns an unsubscribe fn. */
  onMessage(callback: MessageCallback): () => void {
    this.messageListeners.add(callback);
    return () => {
      this.messageListeners.delete(callback);
    };
  }

  /** Register a listener for connection state changes. Returns an unsubscribe fn. */
  onStateChange(callback: StateChangeCallback): () => void {
    this.stateListeners.add(callback);
    return () => {
      this.stateListeners.delete(callback);
    };
  }

  /** Send a structured message to the server. */
  send(data: WSClientMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn(
        "[WebSocketManager] Cannot send message - connection not open",
      );
    }
  }

  // -------------------------------------------------------------------------
  // Internals
  // -------------------------------------------------------------------------

  private createConnection(): void {
    if (!this.projectId) return;

    this.setState("connecting");

    const url = `${this.baseUrl}/ws/${this.projectId}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = this.handleOpen;
    this.ws.onclose = this.handleClose;
    this.ws.onerror = this.handleError;
    this.ws.onmessage = this.handleMessage;
  }

  // -- Event handlers (arrow fns to preserve `this`) --

  private handleOpen = (): void => {
    this.reconnectAttempt = 0;
    this.setState("connected");
    this.startPing();
  };

  private handleClose = (): void => {
    this.stopPing();
    this.setState("disconnected");
    this.scheduleReconnect();
  };

  private handleError = (): void => {
    this.setState("error");
    // onclose will fire after onerror, which triggers reconnect
  };

  private handleMessage = (event: MessageEvent): void => {
    try {
      const message: WSMessage = JSON.parse(event.data as string);

      // Ignore pong messages from keep-alive
      if ((message as unknown as { type: string }).type === "pong") {
        return;
      }

      for (const listener of this.messageListeners) {
        try {
          listener(message);
        } catch (err) {
          console.error("[WebSocketManager] Listener error:", err);
        }
      }
    } catch {
      console.warn("[WebSocketManager] Failed to parse message:", event.data);
    }
  };

  // -- Reconnect logic with exponential backoff --

  private scheduleReconnect(): void {
    if (!this.shouldReconnect) return;

    const delay = Math.min(
      this.baseReconnectDelay * Math.pow(2, this.reconnectAttempt),
      this.maxReconnectDelay,
    );

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempt++;
      this.createConnection();
    }, delay);
  }

  // -- Keep-alive ping --

  private startPing(): void {
    this.stopPing();
    this.pingTimer = setInterval(() => {
      this.send({ action: "ping" });
    }, this.pingInterval);
  }

  private stopPing(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  // -- State management --

  private setState(newState: ConnectionState): void {
    if (this.state === newState) return;
    this.state = newState;

    for (const listener of this.stateListeners) {
      try {
        listener(newState);
      } catch (err) {
        console.error("[WebSocketManager] State listener error:", err);
      }
    }
  }

  // -- Cleanup helpers --

  private clearTimers(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.stopPing();
  }
}

// ---------------------------------------------------------------------------
// Singleton instance for app-wide usage
// ---------------------------------------------------------------------------

let defaultInstance: WebSocketManager | null = null;

/**
 * Returns a shared WebSocketManager singleton.
 * Useful in React components via a custom hook.
 */
export function getWebSocketManager(): WebSocketManager {
  if (!defaultInstance) {
    defaultInstance = new WebSocketManager();
  }
  return defaultInstance;
}

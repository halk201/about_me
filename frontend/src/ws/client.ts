export class WsClient {
  private ws: WebSocket | null = null;
  constructor(private url: string) {}
  connect(onMessage: (data: any) => void): void {
    this.ws = new WebSocket(this.url);
    this.ws.onmessage = (event) => onMessage(JSON.parse(event.data));
  }
  publish(channel: string, payload: Record<string, unknown>): void {
    this.ws?.send(JSON.stringify({ channel, payload }));
  }
}

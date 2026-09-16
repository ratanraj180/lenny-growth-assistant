const BASE_URL = 'http://localhost:8000/api/v1';

export interface Session {
  id: string;
  title: string;
  created_at: string;
}

export interface Source {
  id: number;
  source_id: string;
  title: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

export interface SessionWithMessages extends Session {
  messages: Message[];
}

export const api = {
  getSessions: async (): Promise<Session[]> => {
    const res = await fetch(`${BASE_URL}/sessions/`);
    if (!res.ok) throw new Error('Failed to fetch sessions');
    return res.json();
  },
  
  createSession: async (title: string): Promise<Session> => {
    const res = await fetch(`${BASE_URL}/sessions/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title })
    });
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
  },

  getSession: async (id: string): Promise<SessionWithMessages> => {
    const res = await fetch(`${BASE_URL}/sessions/${id}`);
    if (!res.ok) throw new Error('Failed to fetch session');
    return res.json();
  },

  sendMessage: async (sessionId: string, content: string, provider: string, skill?: string): Promise<Message> => {
    const res = await fetch(`${BASE_URL}/sessions/${sessionId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: 'user', content, provider, skill })
    });
    if (!res.ok) throw new Error('Failed to send message');
    return res.json();
  }
};

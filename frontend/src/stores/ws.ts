import { create } from 'zustand';

export const useWsStore = create<{seq:number;setSeq:(n:number)=>void}>((set)=>({
  seq: 0,
  setSeq: (seq) => set({ seq }),
}));

import { create } from 'zustand';

export const useWalletStore = create<{balance:number;setBalance:(v:number)=>void}>((set)=>({
  balance: 0,
  setBalance: (balance) => set({ balance }),
}));

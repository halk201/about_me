import { create } from 'zustand';

export const useGamesStore = create<{activeGame:string;setActiveGame:(g:string)=>void}>((set)=>({
  activeGame: 'crash',
  setActiveGame: (activeGame) => set({ activeGame }),
}));

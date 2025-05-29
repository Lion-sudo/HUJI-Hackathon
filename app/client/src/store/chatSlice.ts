import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ChatState {
  prompt: string;
  response: string;
  error: string;
  loading: boolean;
}

const initialState: ChatState = {
  prompt: '',
  response: '',
  error: '',
  loading: false,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setPrompt: (state, action: PayloadAction<string>) => {
      state.prompt = action.payload;
    },
    setResponse: (state, action: PayloadAction<string>) => {
      state.response = action.payload;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    clearChat: (state) => {
      state.response = '';
      state.error = '';
    },
  },
});

export const { setPrompt, setResponse, setError, setLoading, clearChat } = chatSlice.actions;
export default chatSlice.reducer; 
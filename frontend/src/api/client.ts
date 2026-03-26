import axios from 'axios';
import type { AxiosError } from 'axios';

export interface AppError {
  message: string;
  status: number;
  detail: string | unknown;
}

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string | unknown }>) => {
    const appError: AppError = {
      message: error.message,
      status: error.response?.status ?? 0,
      detail: error.response?.data?.detail ?? error.message,
    };
    return Promise.reject(appError);
  },
);

export { apiClient };

import axios, {AxiosError, InternalAxiosRequestConfig} from 'axios'
import {auth} from '@/hooks/firebase';

export class ApiError extends Error {
    constructor(
        message: string,
        public status?: number,
        public data?: {
            error?: string;
            detail?: string;
            [key: string]: unknown;
        }
    ) {
        super(message);
        this.name = 'ApiError';
        // This is needed to maintain proper prototype chain in TypeScript
        Object.setPrototypeOf(this, ApiError.prototype);
    }
}

function getCookie(name: string): string | null {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(';').shift() ?? null;
    return null;
}

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true
});

api.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
        try {
            const user = auth.currentUser;
            if (user) {
                const token = await user.getIdToken(true);
                const decodedToken = JSON.parse(atob(token.split('.')[1]));
                const expirationTime = decodedToken.exp * 1000; // Convert to milliseconds

                // If token is close to expiration (within 5 minutes), force refresh
                if (expirationTime - Date.now() < 5 * 60 * 1000) {
                    console.log('Token close to expiration, forcing refresh');
                    const newToken = await user.getIdToken(true);
                    config.headers.Authorization = `Bearer ${newToken}`;
                } else {
                    config.headers.Authorization = `Bearer ${token}`;
                }
            } else {
                console.log('No user found in interceptor');
            }

            const csrfToken = getCookie('csrftoken');
            if (csrfToken) {
                config.headers['X-CSRFToken'] = csrfToken;
            }

            return config;
        } catch (error) {
            // Handle token retrieval errors gracefully
            console.error('Error getting auth token:', error);
            return Promise.reject(new ApiError('Authentication failed', 401));
        }
    },
    (error: AxiosError) => {
        return Promise.reject(new ApiError('Request configuration failed', error.response?.status));
    }
);

api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        // Destructure useful error information
        const {response} = error;

        if (response?.status === 401) {
            try {
                // Sign out the user
                await auth.signOut();

                // Store the intended destination for after login
                sessionStorage.setItem('redirectAfterLogin', window.location.pathname);

                // Redirect to log in
                window.location.href = '/login';

                // Reject with a user-friendly error
                return Promise.reject(
                    new ApiError('Your session has expired. Please log in again.', 401)
                );
            } catch (signOutError) {
                console.error('Error during sign out:', signOutError);
            }
        }

        // Convert all errors to ApiError format for consistent error handling
        return Promise.reject(
            new ApiError(
                error.message || 'An error occurred',
                response?.status,
                response?.data as {
                    error?: string;
                    detail?: string;
                    [key: string]: unknown;
                }
            )
        );
    }
);

export default api;
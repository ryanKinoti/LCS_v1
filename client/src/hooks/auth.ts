import api, {ApiError} from '@/hooks/api.ts';
import {signInWithEmailAndPassword} from "@firebase/auth";
import {User as FirebaseUser} from 'firebase/auth';
import {auth} from '@/hooks/firebase';
import axios from "axios";
import {LoginCredentials, RegistrationData} from "@/lib/types/interfaces/auth";
import {RegisterResponse, UserResponse} from "@/lib/types/interfaces/responses";

export const AuthService = {
    async register(credentials: RegistrationData): Promise<RegisterResponse> {
        try {
            const response = await api.post<RegisterResponse>('/accounts/register/', {
                ...credentials,
                profile_type: 'customer',
            });
            await this.login({
                email: credentials.email,
                password: credentials.password
            });
            return response.data

        } catch (error) {
            if (error instanceof ApiError) {
                console.error('Registration error details:', {
                    status: error.status,
                    data: error.data,
                    message: error.message
                });
                const errorMessage = error.data?.error || error.data?.detail || 'Registration failed';
                throw new Error(errorMessage);
            }
            console.error('Registration error:', error);
            throw new Error('An unexpected error occurred during registration');
        }
    },

    async login(credentials: LoginCredentials): Promise<FirebaseUser> {
        try {
            const userCredential = await signInWithEmailAndPassword(
                auth,
                credentials.email,
                credentials.password
            );
            await userCredential.user.getIdToken(true);
            console.log('logged in user:', userCredential.user);
            return userCredential.user;
        } catch (error) {
            if (error instanceof ApiError) {
                console.error('Registration error details:', {
                    status: error.status,
                    data: error.data,
                    message: error.message
                });
                const errorMessage = error.data?.error || error.data?.detail || 'Login failed';
                throw new Error(errorMessage);
            }
            console.error('Login error:', error);
            throw new Error('An unexpected error occurred during logging in');
        }

    },

    async logout() {
        try {
            await auth.signOut();
        } catch (error) {
            console.error('Logout failed:', error);
            throw new Error('Failed to logout');
        }
    },

    async getCurrentUser(): Promise<UserResponse | null> {
        try {
            const response = await api.get<UserResponse>('/accounts/user/me/');
            console.log('current user:', response.data);
            return response.data;
        } catch (error) {
            if (error instanceof ApiError) {
                if (error.status === 401) {
                    // User is not authenticated
                    return null;
                }
                throw new Error(error.data?.detail || 'Failed to fetch user profile');
            }
            throw new Error('An unexpected error occurred while fetching user profile');
        }
    },

    async redirectToDjangoAdmin() {
        try {
            const user = auth.currentUser;
            if (!user) {
                throw new Error('No authenticated user');
            }
            const token = await user.getIdToken(true);
            const apiBaseUrl = import.meta.env.VITE_API_URL;

            await api.get('/accounts/admin-session/', {
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                withCredentials: true
            });

            await new Promise(resolve => setTimeout(resolve, 100));

            const response = await api.post('/accounts/admin-session/', {}, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                withCredentials: true
            });

            if (response.status === 200) {
                await new Promise(resolve => setTimeout(resolve, 100));

                const adminUrl = apiBaseUrl.replace('localhost', '127.0.0.1');
                window.location.href = `${adminUrl}/admin/`;
            }
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.error || 'Failed to access admin panel');
            }
            if (error instanceof Error) {
                throw new Error(error.message);
            }
            throw new Error('Failed to access admin panel');
        }
    },
};
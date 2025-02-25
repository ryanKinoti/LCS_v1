import {createContext, useContext, useEffect, useState, ReactNode, useCallback} from 'react';
import {auth} from '@/hooks/firebase';
import {AuthService} from '@/hooks/auth.ts';
import {Loader2} from "lucide-react";
import {
    AuthContextType,
    AuthState,
    AuthActions
} from "@/lib/types/interfaces/auth.ts";
import { DashboardResponse } from '@/lib/types/interfaces/responses';

interface AuthProviderProps {
    children: ReactNode;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({children}: AuthProviderProps) {

    const [state, setState] = useState<AuthState>({
        firebaseUser: null,
        user: null,
        dashboardData: null,
        status: 'idle',
        initialized: false
    });

    const updateState = useCallback((updates: Partial<AuthState>) => {
        setState(current => ({...current, ...updates}));
    }, []);

    const fetchUserProfile = useCallback(async () => {
        try {
            updateState({
                status: 'authenticating',
            });
            const userProfile = await AuthService.getCurrentUser();
            await AuthService.getDashboardData();
            if (userProfile) {
                updateState({
                    user: userProfile,
                    status: 'authenticated',
                    initialized: true
                });
            } else {
                throw new Error("User profile not found");
            }
        } catch (error) {
            console.error('Error fetching user profile:', error);
            await AuthService.logout();
            updateState({user: null, firebaseUser: null, status: 'error', initialized: true});
        }
    }, [updateState]);

    const fetchDashboard = useCallback(async (): Promise<DashboardResponse | null> => {
        try {
            updateState({ status: 'authenticating' });
            const dashboardResponse = await AuthService.getDashboardData();

            if (dashboardResponse && dashboardResponse.dashboard) {
                updateState({
                    dashboardData: dashboardResponse.dashboard,
                    status: 'authenticated'
                });
                return dashboardResponse;
            }

            updateState({ status: 'authenticated' });
            return null;
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            updateState({ status: 'error' });
            return null;
        }
    }, [updateState]);

    useEffect(() => {
        const unsubscribe = auth.onAuthStateChanged(async (firebaseUser) => {
            updateState({firebaseUser});
            if (firebaseUser) {
                await fetchUserProfile();
            } else {
                updateState({
                    user: null,
                    dashboardData: null,
                    status: 'idle',
                    initialized: true
                });
            }
        });
        // Cleanup subscription
        return () => unsubscribe();
    }, [fetchUserProfile, updateState]);

    const actions: AuthActions = {
        login: async (credentials) => {
            updateState({status: 'authenticating',});
            try {
                await AuthService.login(credentials);
            } catch (error) {
                updateState({status: 'error'});
                throw error;
            }
        },

        register: async (credentials) => {
            updateState({status: 'authenticating',});
            try {
                await AuthService.register(credentials);
            } catch (error) {
                updateState({status: 'error'});
                throw error;
            }
        },

        logout: async () => {
            updateState({status: 'authenticating'});
            try {
                await AuthService.logout();
            } catch (error) {
                updateState({status: 'error'});
                throw error;
            }
        },

        refreshUser: async () => {
            if (state.firebaseUser) {
                await fetchUserProfile();
            }
        },

        fetchDashboard,
    };

    const contextValue: AuthContextType = {
        ...state,
        ...actions
    };

    if (!state.initialized) {
        return (
            <div className="flex items-center justify-center h-screen">
                <Loader2 className="h-8 w-8 animate-spin"/>
            </div>
        );
    }

    return (
        <AuthContext.Provider value={contextValue}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === null) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
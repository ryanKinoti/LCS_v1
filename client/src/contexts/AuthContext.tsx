import {createContext, useContext, useEffect, useState, ReactNode, useCallback} from 'react';
import {auth} from '@/hooks/firebase';
import {User as FirebaseUser} from 'firebase/auth';
import {AuthService, UserResponse as BackendUser, LoginCredentials, RegisterCredentials} from '@/hooks/auth.ts';
import {Loader2} from "lucide-react";

interface AuthState {
    firebaseUser: FirebaseUser | null;    // Firebase authentication state
    user: BackendUser | null;             // Backend user data
    status: 'idle' | 'authenticating' | 'authenticated' | 'error';
    initialized: boolean;                  // Whether auth system has completed initial load
}

interface AuthActions {
    login: (credentials: LoginCredentials) => Promise<void>;
    register: (credentials: RegisterCredentials) => Promise<void>;
    logout: () => Promise<void>;
    refreshUser: () => Promise<void>;
}

interface AuthContextType extends AuthState, AuthActions {
}

interface AuthProviderProps {
    children: ReactNode;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({children}: AuthProviderProps) {

    const [state, setState] = useState<AuthState>({
        firebaseUser: null,
        user: null,
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
            if (userProfile) {
                updateState({
                    user: userProfile,
                    status: 'authenticated',
                    initialized: true
                });
            }
        } catch (error) {
            console.error('Error fetching user profile:', error);
            await AuthService.logout();
            updateState({user: null, firebaseUser: null, status: 'error', initialized: true});
        }
    }, [updateState]);

    useEffect(() => {
        const unsubscribe = auth.onAuthStateChanged(async (firebaseUser) => {
            if (firebaseUser) {
                await fetchUserProfile();
            } else {
                updateState({
                    firebaseUser: null,
                    user: null,
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
                updateState({ status: 'error' });
                throw error;
            }
        },

        register: async (credentials) => {
            updateState({status: 'authenticating',});
            try {
                await AuthService.register(credentials);
            } catch (error) {
                updateState({ status: 'error' });
                throw error;
            }
        },

        logout: async () => {
            updateState({ status: 'authenticating' });
            try {
                await AuthService.logout();
            } catch (error) {
                updateState({ status: 'error' });
                throw error;
            }
        },

        refreshUser: async () => {
            if (state.firebaseUser) {
                await fetchUserProfile();
            }
        }
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
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
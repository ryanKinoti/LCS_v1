import React, { ReactNode } from 'react';
import { AuthProvider } from "@/contexts/AuthContext";
import { NotificationProvider } from "@/contexts/NotificationContext";
import { ModalProvider } from "@/contexts/ModalContext";
import { Toaster } from "@/components/ui/toaster";

interface AppProvidersProps {
    children: ReactNode;
}

export const AppProviders: React.FC<AppProvidersProps> = ({ children }) => {
    return (
        <AuthProvider>
            <NotificationProvider>
                <ModalProvider>
                    {children}
                    <Toaster />
                </ModalProvider>
            </NotificationProvider>
        </AuthProvider>
    );
};
import {createContext, useContext} from "react";
import {NotificationContextType, NotificationProviderProps, ToastOptions} from '@/lib/types/interfaces/common';
import {ToastType} from "@/lib/types/constants/declarations";
import {toast} from "@/hooks/use-toast";
import {ToastAction} from "@/components/ui/toast";

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<NotificationProviderProps> = ({children}) => {

    const getToastStyling = (type: ToastType) => {
        switch (type) {
            case ToastType.SUCCESS:
                return {className: 'bg-[#28A745] text-white'};
            case ToastType.ERROR:
                return {className: 'bg-[#DC3545] text-white'};
            case ToastType.WARNING:
                return {className: 'bg-[#FFC107] text-[#333333]'};
            case ToastType.INFO:
                return {className: 'bg-[#0066FF] text-white'};
            default:
                return {className: 'bg-[#F8F9FA] text-[#343A40]'};
        }
    };

    const showToast = (
        message: string,
        type: ToastType = ToastType.DEFAULT,
        options?: ToastOptions
    ) => {
        const styling = getToastStyling(type);

        toast({
            title: message,
            description: options?.description,
            duration: options?.duration || 3000,
            ...styling,
            action: options?.action ? (
                <ToastAction altText={options.action.label} onClick={options.action.onClick}>
                    {options.action.label}
                </ToastAction>
            ) : undefined,
        });
    };

    const showActionToast = (
        message: string,
        actionLabel: string,
        onAction: () => void,
        type: ToastType = ToastType.DEFAULT,
        options?: ToastOptions
    ) => {
        showToast(message, type, {
            ...options,
            action: {
                label: actionLabel,
                onClick: onAction,
            },
        });
    };

    const copyToClipboard = async (text: string, successMessage: string = 'Copied to clipboard!') => {
        try {
            await navigator.clipboard.writeText(text);
            showToast(successMessage, ToastType.SUCCESS);
        } catch (err) {
            console.error('Failed to copy to clipboard:', err);
            showToast('Failed to copy to clipboard', ToastType.ERROR);
        }
    };

    return (
        <NotificationContext.Provider value={{showToast, showActionToast, copyToClipboard}}>
            {children}
        </NotificationContext.Provider>
    );

};

export const useNotification = (): NotificationContextType => {
    const context = useContext(NotificationContext);
    if (context === undefined) {
        throw new Error('useNotification must be used within a NotificationProvider');
    }
    return context;
};
import {ContactMethodTypes, ToastType, UserRoleTypes} from "@/lib/types/constants/declarations.ts";
import {ReactNode} from "react";

// common user interfaces
export interface DailySchedule {
    start: string; // Format: "HH:mm"
    end: string;   // Format: "HH:mm"
}

export interface WeeklyAvailability {
    monday?: DailySchedule;
    tuesday?: DailySchedule;
    wednesday?: DailySchedule;
    thursday?: DailySchedule;
    friday?: DailySchedule;
}

interface RootUser {
    id: number;
    email: string;
    full_name: string;
}

interface BaseUser extends RootUser {
    firebase_uid?: string;
    first_name: string;
    last_name: string;
    phone_number?: string;
    email_verified: boolean;
    phone_verified: boolean;
    created_at: string;
    updated_at: string;
}

interface CustomerProfile {
    role: Extract<UserRoleTypes, UserRoleTypes.CLIENT | UserRoleTypes.COMPANY>;
    company_name?: string;
    preferred_contact: Extract<ContactMethodTypes, ContactMethodTypes.EMAIL | ContactMethodTypes.PHONE_CALL | ContactMethodTypes.SMS>;
    address?: string;
    notes?: string;
    login_token?: string;
}

interface StaffProfile {
    role: Extract<UserRoleTypes, UserRoleTypes.ADMIN | UserRoleTypes.TECHNICIAN | UserRoleTypes.RECEPTIONIST>;
    specializations: string[];
    availability: WeeklyAvailability;
    login_token?: string;
}

interface CustomerUser extends BaseUser {
    profile_type: 'customer';
    customer_profile: CustomerProfile;
    staff_profile?: never;
}

interface StaffUser extends BaseUser {
    profile_type: 'staff';
    staff_profile: StaffProfile;
    customer_profile?: never;
}

// common UI interfaces
// 1. Toasts
interface ToastOptions {
    duration?: number;
    action?: {
        label: string;
        onClick: () => void;
    };
    description?: string;
}

interface NotificationContextType {
    showToast: (message: string, type?: ToastType, options?: ToastOptions) => void;
    showActionToast: (message: string, actionLabel: string, onAction: () => void, type?: ToastType, options?: ToastOptions) => void;
    copyToClipboard: (text: string, successMessage?: string) => void;
}

interface NotificationProviderProps {
    children: ReactNode;
}

//2. Modals
interface BaseModalProps {
    title: string;
    description?: string;
    onClose: () => void;
}

interface ConfirmationModalProps extends BaseModalProps {
    type: 'confirmation';
    confirmLabel?: string;
    cancelLabel?: string;
    onConfirm: () => void;
    isDangerous?: boolean;
}

interface FormModalProps extends BaseModalProps {
    type: 'form';
    formContent: ReactNode;
    submitLabel?: string;
    onSubmit: () => void;
}

interface AlertModalProps extends BaseModalProps {
    type: 'alert';
    alertType?: 'info' | 'warning' | 'error' | 'success';
}

interface CustomModalProps extends BaseModalProps {
    type: 'custom';
    content: ReactNode;
}

interface ModalProviderProps {
    children: ReactNode;
}

interface ModalContextType {
    currentModal: ModalProps | null;
    showConfirmationModal: (props: Omit<ConfirmationModalProps, 'type'>) => void;
    showFormModal: (props: Omit<FormModalProps, 'type'>) => void;
    showAlertModal: (props: Omit<AlertModalProps, 'type'>) => void;
    showCustomModal: (props: Omit<CustomModalProps, 'type'>) => void;
    closeModal: () => void;
}


export type User = CustomerUser | StaffUser;
export type ModalProps = | ConfirmationModalProps | FormModalProps | AlertModalProps | CustomModalProps;
export type {
    ConfirmationModalProps,
    FormModalProps,
    AlertModalProps,
    CustomModalProps,
    ModalProviderProps,
    ModalContextType,

    ToastOptions,
    NotificationContextType,
    NotificationProviderProps
};
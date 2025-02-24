import {BaseEntity, WeeklyAvailability} from "@/lib/types/common";

export type CustomerRole = 'client' | 'company';
export type StaffRole = 'technician' | 'admin' | 'receptionist';
export type ContactMethod = 'email' | 'phone_call' | 'sms';

export interface User extends BaseEntity {
    email: string;
    first_name: string;
    last_name: string;
    phone_number?: string;
    email_verified: boolean;
    phone_verified: boolean;
    is_staff: boolean;
    is_superuser: boolean;
    firebase_uid?: string;
}

interface LoginCredentials {
    email: string;
    password: string;
}

interface RegistrationData {
    email: string;
    password: string;
    confirm_password: string;
    first_name: string;
    last_name: string;
    phone_number?: string;
    profile_type: 'staff' | 'customer';
    role: CustomerRole | StaffRole;
    company_name?: string;
}

export interface CustomerProfile extends BaseEntity {
    user: User;
    role: CustomerRole;
    preferred_contact: ContactMethod;
    company_name?: string;
    login_token?: string;
    address?: string;
    notes?: string;
}

export interface StaffProfile extends BaseEntity {
    user: User;
    role: StaffRole;
    specializations: string[];
    availability: WeeklyAvailability;
    login_token?: string;
}

export interface PasswordChangeData {
    old_password: string;
    new_password: string;
}

export interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (credentials: LoginCredentials) => Promise<void>;
    logout: () => Promise<void>;
    register: (data: RegistrationData) => Promise<void>;
}
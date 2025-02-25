import {WeeklyAvailability} from "@/lib/types/interfaces/common";
import {ContactMethodTypes, UserRoleTypes} from "@/lib/types/constants/declarations";
import {User as FirebaseUser} from "@firebase/auth";
import {DashboardResponse, UserResponse} from "@/lib/types/interfaces/responses";
import {AdminDashboardData, CustomerDashboardData, StaffDashboardData} from "@/lib/types/interfaces/dashboards";

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface BaseRegistrationData {
    email: string;
    password: string;
    confirm_password: string;
    first_name: string;
    last_name: string;
    phone_number?: string;
}

export interface CustomerRegistrationData extends BaseRegistrationData {
    profile_type: 'customer';
    role: Extract<UserRoleTypes, UserRoleTypes.CLIENT | UserRoleTypes.COMPANY>;
    company_name?: string;
    preferred_contact?: Extract<ContactMethodTypes, ContactMethodTypes.EMAIL | ContactMethodTypes.PHONE_CALL | ContactMethodTypes.SMS>;
}

export interface StaffRegistrationData extends BaseRegistrationData {
    profile_type: 'staff';
    role: Extract<UserRoleTypes, UserRoleTypes.ADMIN | UserRoleTypes.TECHNICIAN | UserRoleTypes.RECEPTIONIST>;
    specializations: string[];
    availability?: WeeklyAvailability;
}

export interface AuthState {
    firebaseUser: FirebaseUser | null;    // Firebase authentication state
    user: UserResponse  | null;             // Backend user data
    dashboardData: AdminDashboardData | StaffDashboardData | CustomerDashboardData | null; // Dashboard data
    status: 'idle' | 'authenticating' | 'authenticated' | 'error';
    initialized: boolean;                  // Whether auth system has completed initial load
}

export interface AuthActions {
    login: (credentials: LoginCredentials) => Promise<void>;
    register: (credentials: RegistrationData) => Promise<void>;
    logout: () => Promise<void>;
    refreshUser: () => Promise<void>;
    fetchDashboard: () => Promise<DashboardResponse | null>;
}

export interface AuthContextType extends AuthState, AuthActions {}

export type RegistrationData = CustomerRegistrationData | StaffRegistrationData;
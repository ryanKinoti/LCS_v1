import {ContactMethodTypes, UserRoleTypes} from "@/lib/types/constants/declarations.ts";

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

export type User = CustomerUser | StaffUser;
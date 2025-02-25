import {User} from "@/lib/types/interfaces/common";
import {UserRoleTypes} from "@/lib/types/constants/declarations.ts";

// import {Dashboard} from "@/lib/types/interfaces/dashboards";


export interface UserResponse {
    user: User;
    profile?: {
        id?: number;
        role?: string;
        specializations?: string[];
    };
    role: Extract<UserRoleTypes, UserRoleTypes.ADMIN | UserRoleTypes.STAFF | UserRoleTypes.CUSTOMER>;
}

export interface RegisterResponse {
    message: string;
    data: {
        email: string;
        login_token: string;
    };
}
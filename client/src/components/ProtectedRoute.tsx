import {Navigate, useLocation} from 'react-router-dom';
import {useAuth} from '@/contexts/AuthContext';
import {Loader2} from 'lucide-react';
import {UserRoleTypes} from "@/lib/types/constants/declarations";
import {UserResponse} from "@/lib/types/interfaces/responses.ts";

interface ProtectedRouteProps {
    children: React.ReactNode;
    allowedRoles?: UserRoleTypes[];
}

export const ProtectedRoute = ({children, allowedRoles = []}: ProtectedRouteProps) => {
    const {user, status, initialized} = useAuth();
    const location = useLocation();

    if (!initialized || status === 'authenticating') {
        return (
            <div className="flex items-center justify-center h-screen">
                <Loader2 className="h-8 w-8 animate-spin"/>
            </div>
        );
    }

    if (status === 'idle' || status === 'error') {
        sessionStorage.setItem('redirectAfterLogin', location.pathname);
        return <Navigate to="/login" replace state={{from: location}}/>;
    }

    const userRole = getUserRole(user);

    if (!userRole) {
        return <Navigate to="/login" replace/>;
    }

    if (allowedRoles.length > 0 && !allowedRoles.includes(userRole)) {
        return <Navigate to={getDashboardPath(userRole)} replace/>;
    }

    return <>{children}</>;
};

function getDashboardPath(role: string): string {
    switch (role) {
        case 'admin':
            return '/admin/dashboard';
        case 'staff':
            return '/staff/dashboard';
        case 'customer':
            return '/customer/dashboard';
        default:
            return '/';
    }
}

function getUserRole(user: UserResponse | null): UserRoleTypes | undefined {
    if (!user) return undefined;
    return user.role;
}

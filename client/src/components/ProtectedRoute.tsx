import {Navigate, useLocation} from 'react-router-dom';
import {useAuth} from '@/contexts/AuthContext';
import {Loader2} from 'lucide-react';

interface ProtectedRouteProps {
    children: React.ReactNode;
    allowedRoles?: ('admin' | 'staff' | 'customer')[];
}

export const ProtectedRoute = ({children, allowedRoles = []}: ProtectedRouteProps) => {
    const {user, loading, initialized} = useAuth();
    const location = useLocation();

    if (!initialized || loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <Loader2 className="h-8 w-8 animate-spin"/>
            </div>
        );
    }

    if (!user) {
        sessionStorage.setItem('redirectAfterLogin', location.pathname);
        return <Navigate to="/" replace state={{from: location}}/>;
    }

    if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
        if (!allowedRoles.includes(user.role)) {
            return <Navigate to={getDashboardPath(user.role)} replace/>;
        }
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
import React from 'react';
import {Link, useNavigate} from 'react-router-dom';
import {Button} from '@/components/ui/button';
import {LogOut, User} from 'lucide-react';
import {useAuth} from "@/contexts/AuthContext.tsx";

interface NavigationProps {
    logoSrc: string;
}

const Navigation: React.FC<NavigationProps> = ({logoSrc}) => {
    const {user, logout} = useAuth();
    const navigate = useNavigate();

    const getDashboardRoute = () => {
        if (!user) return '/';

        switch (user.role) {
            case 'admin':
                return '/admin/dashboard';
            case 'staff':
                return '/staff/dashboard';
            case 'customer':
                return '/customer/dashboard';
            default:
                return '/';
        }
    };

    const handleLogout = async () => {
        try {
            await logout();
            navigate('/');
        } catch (error) {
            console.error('Logout failed:', error);
            // You might want to show an error toast here
        }
    };

    const getDisplayName = () => {
        if (!user?.user) return '';
        return user.user.full_name || `${user.user.first_name} ${user.user.last_name}`;
    };

    return (
        <header className="flex items-center justify-between border-b border-[#f0f3f4] px-10 py-3">
            <div className="flex items-center gap-4">
                <img src={logoSrc} alt="Laptop Care" className="h-12"/>
            </div>

            <nav className="flex flex-1 justify-end gap-8">
                <div className="flex items-center gap-9">
                    <a className="text-sm font-medium text-[#111517] hover:text-[#0066FF]" href="/">
                        Services
                    </a>
                    <a className="text-sm font-medium text-[#111517] hover:text-[#0066FF]" href="/">
                        Why Us
                    </a>
                    <a className="text-sm font-medium text-[#111517] hover:text-[#0066FF]" href="/">
                        Reviews
                    </a>
                    <a className="text-sm font-medium text-[#111517] hover:text-[#0066FF]" href="/">
                        Contact
                    </a>
                </div>

                <div className="flex items-center gap-2">
                    {user ? (
                        <>
                            <Button variant="outline" asChild>
                                <Link to={getDashboardRoute()}>
                                    <User className="mr-2 h-4 w-4"/>
                                    {getDisplayName()}
                                </Link>
                            </Button>
                            <Button variant="default" onClick={handleLogout}>
                                <LogOut className="mr-2 h-4 w-4"/>
                                Sign Out
                            </Button>
                        </>
                    ) : (
                        <>
                            <Button variant="outline" asChild>
                                <Link to="/register">Sign Up</Link>
                            </Button>
                            <Button variant="default" asChild>
                                <Link to="/login">Log In</Link>
                            </Button>
                        </>
                    )}
                </div>
            </nav>
        </header>
    );
};

export default Navigation;
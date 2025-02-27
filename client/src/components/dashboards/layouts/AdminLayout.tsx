import {useState} from 'react';
import {
    LayoutDashboard,
    Users,
    Laptop,
    Package,
    // Bell,
    // Settings,
    // FileText,
    // DollarSign,
    ChevronLeft,
    Menu, LogOut, HandHelping, SquareUserRound
} from 'lucide-react';
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {useToast} from "@//hooks/use-toast";
import {ToastAction} from "@/components/ui/toast"
import logoMain from "@/assets/lcs_main_logo.png";
import {Button} from "@/components/ui/button";
import {Link, useNavigate} from "react-router-dom";
import {AuthService} from "@/hooks/auth.ts"
import {useAuth} from "@/contexts/AuthContext.tsx";
import {AdminLayoutProps} from "@/lib/types/interfaces/dashboards.ts";
import {ToastType} from "@/lib/types/constants/declarations.ts";
import {useNotification} from "@/contexts/NotificationContext.tsx";

const AdminLayout = ({children, activeTab, onTabChange, isLoading: propIsLoading = false}: AdminLayoutProps) => {
    const {fetchDashboard, logout, status} = useAuth();
    const navigate = useNavigate();
    const [collapsed, setCollapsed] = useState(false);
    const [isRedirecting, setIsRedirecting] = useState(false);
    const [showConfirmDialog, setShowConfirmDialog] = useState(false);
    const {toast} = useToast();
    const {showToast} = useNotification();
    const isLoading = propIsLoading || status === 'authenticating' || isRedirecting;

    const handleDjangoAdminRedirect = async () => {
        setIsRedirecting(true);
        try {
            await AuthService.redirectToDjangoAdmin()
        } catch (error) {
            console.error('Failed to redirect to Django admin:', error)
        } finally {
            setIsRedirecting(false);
            setShowConfirmDialog(false);
        }
    }

    const handleLogout = async () => {
        try {
            await logout();
            showToast("Logged out successfully", ToastType.SUCCESS);
            navigate('/login');
        } catch (error) {
            console.error('Logout failed:', error);
            toast({
                title: "Logout Failed",
                description: `An error occurred while logging out: ${error instanceof Error ? error.message : 'Unknown error'}`,
                action: <ToastAction altText="Try again">Try again</ToastAction>,
                variant: "destructive"
            });
        }
    };

    const handleNavItemClick = async (tabId: string) => {
        onTabChange(tabId);
        try {
            await fetchDashboard();
        } catch (error) {
            console.error('Failed to refresh dashboard data:', error);
            toast({
                title: "Data Refresh Failed",
                description: "Unable to refresh dashboard data. Some information may be outdated.",
                variant: "destructive"
            });
        }
    };

    const navItems = [
        {title: 'Overview', icon: <LayoutDashboard size={20}/>, id: 'overview'},
        {title: 'Inventory', icon: <Package size={20}/>, id: 'inventory'},
        {title: 'Services', icon: <HandHelping size={20}/>, id: 'services'},
        {title: 'Bookings', icon: <Laptop size={20}/>, id: 'bookings'},
        {title: 'Staff', icon: <SquareUserRound size={20}/>, id: 'staff'},
        {title: 'Customers', icon: <Users size={20}/>, id: 'clients'},
        // {title: 'Reports', icon: <FileText size={20}/>, id: 'reports'},
        // {title: 'Finance', icon: <DollarSign size={20}/>, id: 'finance'},
        // {title: 'Notifications', icon: <Bell size={20}/>, id: 'notifications'},
        // {title: 'Settings', icon: <Settings size={20}/>, id: 'settings'}
    ];

    return (
        <div className="flex h-screen bg-[#F8F9FA]">
            <aside className={`bg-[#004085] text-white transition-all duration-300 ${
                collapsed ? 'w-16' : 'w-64'}`}>
                <div className="p-4 flex items-center justify-between">
                    {!collapsed &&
                        <div className="font-bold text-lg">
                            <Link to="/">
                                <img src={logoMain || "/placeholder.svg"} alt="Laptop Care"
                                     className="h-16 mx-auto bg-white"/>
                            </Link>
                        </div>
                    }
                    <button
                        onClick={() => setCollapsed(!collapsed)}
                        className="p-1 hover:bg-[#003366] rounded">
                        {collapsed ? <Menu size={20}/> : <ChevronLeft size={20}/>}
                    </button>
                </div>

                <nav className="mt-4">
                    {navItems.map((item) => (
                        <button
                            key={item.id}
                            onClick={() => handleNavItemClick(item.id)}
                            disabled={isLoading}
                            className={`w-full flex items-center px-4 py-3 transition-colors ${
                                activeTab === item.id
                                    ? 'bg-[#003366]'
                                    : 'hover:bg-[#003366]'
                            }${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}>
                            <span className="mr-3">{item.icon}</span>
                            {!collapsed && <span>{item.title}</span>}
                        </button>
                    ))}
                </nav>
            </aside>

            <div className="flex-1 flex flex-col overflow-hidden">
                <header className="bg-[#004085] text-white border-b border-gray-200 p-4">
                    <div className="flex items-center justify-between">
                        <h1 className="text-2xl font-bold">Laptop Care Admin Dashboard</h1>
                        <Button variant={"default"} onClick={() => setShowConfirmDialog(true)}>
                            {isLoading ? "Redirecting..." : "Django Admin"}
                        </Button>
                        <Button variant="default" size="sm" onClick={handleLogout}>
                            <LogOut className="mr-2 h-4 w-4"/>
                            Logout
                        </Button>
                        <AlertDialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
                            <AlertDialogContent>
                                <AlertDialogHeader>
                                    <AlertDialogTitle>Switch to Django Admin</AlertDialogTitle>
                                    <AlertDialogDescription>
                                        You are about to be redirected to the Django administration interface.
                                        Do you want to continue?
                                    </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                                    <AlertDialogAction onClick={handleDjangoAdminRedirect}>
                                        Continue
                                    </AlertDialogAction>
                                </AlertDialogFooter>
                            </AlertDialogContent>
                        </AlertDialog>
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto p-4">
                    {children}
                </main>
            </div>
        </div>
    );
};

export default AdminLayout;
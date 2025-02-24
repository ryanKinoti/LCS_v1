import React, {ReactElement, useMemo} from 'react';
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer} from 'recharts';
import {
    Users,
    Laptop,
    Package,
    AlertCircle,
    Calendar,
    Bell,
    Settings,
    Loader2,
} from 'lucide-react';
import {useAuth} from '@/contexts/AuthContext';
import {formatDistance} from 'date-fns';
import {AdminDashboard, CustomerDashboard, StaffDashboard} from "@/hooks/auth.ts";

function isAdminDashboard(dashboard: unknown): dashboard is AdminDashboard {
    if (!dashboard || typeof dashboard !== 'object') {
        return false;
    }
    return dashboard && 'total_inventory_value' in dashboard;
}

function isStaffDashboard(dashboard: unknown): dashboard is StaffDashboard {
    if (!dashboard || typeof dashboard !== 'object') {
        return false;
    }
    return dashboard && 'assigned_repairs' in dashboard;
}

function isCustomerDashboard(dashboard: unknown): dashboard is CustomerDashboard {
    if (!dashboard || typeof dashboard !== 'object') {
        return false;
    }
    return dashboard && 'registered_devices' in dashboard;
}

const Overview = () => {
    const {user} = useAuth();

    const revenueChartData = useMemo(() => {
        if (!user?.dashboard) return [];
        const dashboard = user.dashboard;
        if (isAdminDashboard(dashboard)) {
            return [{
                month: 'Current',
                amount: dashboard.revenue_data.total_revenue
            }];
        }
        return [];
    }, [user?.dashboard]);

    if (!user) {
        return (
            <div className="flex items-center justify-center h-screen">
                <Loader2 className="h-8 w-8 animate-spin"/>
            </div>
        );
    }

    const {dashboard, role} = user;

    let typedDashboard: AdminDashboard | StaffDashboard | CustomerDashboard;
    if (role === 'admin' && isAdminDashboard(dashboard)) {
        typedDashboard = dashboard;
    } else if (role === 'staff' && isStaffDashboard(dashboard)) {
        typedDashboard = dashboard;
    } else if (role === 'customer' && isCustomerDashboard(dashboard)) {
        typedDashboard = dashboard;
    } else {
        // Handle unexpected dashboard type
        console.error('Dashboard type does not match user role');
        return (
            <div className="flex items-center justify-center h-screen">
                <div>Error: Invalid dashboard type</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#F8F9FA]">
            <main className="container mx-auto p-4">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    {isAdminDashboard(typedDashboard) && (
                        <>
                            <StatCard
                                title="Total Repairs"
                                value={typedDashboard.total_repairs}
                                icon={<Laptop className="h-6 w-6"/>}
                                color="#0066FF"/>
                            <StatCard
                                title="Pending Repairs"
                                value={typedDashboard.pending_repairs}
                                icon={<AlertCircle className="h-6 w-6"/>}
                                color="#DC3545"/>
                            <StatCard
                                title="Low Stock Items"
                                value={typedDashboard.low_stock_items}
                                icon={<Package className="h-6 w-6"/>}
                                color="#28A745"/>
                            <StatCard
                                title="Active Staff"
                                value={typedDashboard.active_staff}
                                icon={<Users className="h-6 w-6"/>}
                                color="#FFC107"/>
                        </>
                    )}

                    {isStaffDashboard(typedDashboard) && (
                        <>
                            <StatCard
                                title="Assigned Repairs"
                                value={typedDashboard.assigned_repairs}
                                icon={<Laptop/>}
                                color="#0066FF"
                            />
                            <StatCard
                                title="Pending Repairs"
                                value={typedDashboard.pending_repairs}
                                icon={<AlertCircle/>}
                                color="#DC3545"
                            />
                            <StatCard
                                title="Completed Repairs"
                                value={typedDashboard.completed_repairs}
                                icon={<Package/>}
                                color="#28A745"
                            />
                        </>
                    )}

                    {isCustomerDashboard(typedDashboard) && (
                        <>
                            <StatCard
                                title="Total Bookings"
                                value={typedDashboard.total_bookings}
                                icon={<Calendar/>}
                                color="#0066FF"
                            />
                            <StatCard
                                title="Active Bookings"
                                value={typedDashboard.active_bookings}
                                icon={<AlertCircle/>}
                                color="#DC3545"
                            />
                            <StatCard
                                title="Registered Devices"
                                value={typedDashboard.registered_devices}
                                icon={<Laptop/>}
                                color="#28A745"
                            />
                        </>
                    )}
                </div>

                {/* Charts and Additional Info */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Revenue Chart (Admin Only) */}
                    {isAdminDashboard(typedDashboard) && revenueChartData.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Revenue Overview</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="h-72">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={revenueChartData}>
                                            <CartesianGrid strokeDasharray="3 3"/>
                                            <XAxis dataKey="month"/>
                                            <YAxis/>
                                            <Tooltip/>
                                            <Line
                                                type="monotone"
                                                dataKey="amount"
                                                stroke="#0066FF"
                                                strokeWidth={2}
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Recent Activity */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Recent Activity</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {typedDashboard.recent_activity.map((activity, index) => (
                                    <div key={`${activity.type}-${activity.id}-${index}`}
                                         className="flex items-start space-x-4">
                                        <div className="rounded-full p-2 bg-blue-100">
                                            {activity.type === 'booking' ? (
                                                <Calendar className="h-4 w-4 text-blue-600"/>
                                            ) : (
                                                <Package className="h-4 w-4 text-blue-600"/>
                                            )}
                                        </div>
                                        <div className="flex-1">
                                            <p className="text-sm text-gray-800">{activity.action}</p>
                                            <p className="text-xs text-gray-500">
                                                {formatDistance(new Date(activity.timestamp), new Date(), {addSuffix: true})}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Quick Actions */}
                    {isAdminDashboard(typedDashboard) && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Quick Actions</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="flex flex-wrap gap-4">
                                    <QuickActionButton
                                        icon={<Calendar/>}
                                        label="New Booking"
                                        onClick={() => window.location.href = '/admin/bookings/new'}/>
                                    <QuickActionButton
                                        icon={<Package/>}
                                        label="Add Inventory"
                                        onClick={() => window.location.href = '/admin/inventory/new'}/>
                                    <QuickActionButton
                                        icon={<Bell/>}
                                        label="Notifications"
                                        onClick={() => window.location.href = '/admin/notifications'}/>
                                    <QuickActionButton
                                        icon={<Settings/>}
                                        label="Settings"
                                        onClick={() => window.location.href = '/admin/settings'}/>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </div>
            </main>
        </div>
    );
};

// Stat Card Component
interface StatCardProps {
    title: string;
    value: number;
    icon: ReactElement;
    color: string;
}

const StatCard: React.FC<StatCardProps> = ({title, value, icon, color}) => (
    <Card>
        <CardContent className="flex items-center p-4">
            <div
                className="rounded-full p-3 mr-4"
                style={{backgroundColor: `${color}20`}}>
                {React.cloneElement(icon, {color} as React.SVGProps<SVGSVGElement>)}
            </div>
            <div>
                <p className="text-sm text-gray-600">{title}</p>
                <p className="text-2xl font-bold text-[#343A40]">{value}</p>
            </div>
        </CardContent>
    </Card>
);

// Quick Action Button Component
interface QuickActionButtonProps {
    icon: ReactElement;
    label: string;
    onClick: () => void;
}

const QuickActionButton: React.FC<QuickActionButtonProps> = ({icon, label, onClick}) => (
    <button
        onClick={onClick}
        className="flex items-center justify-center p-4 bg-[#F4F6F8] hover:bg-[#E2E6EA] rounded-lg transition-colors duration-200">
        <div className="flex flex-col items-center">
            {React.cloneElement(icon, {
                className: "h-6 w-6 mb-2 text-[#004085]",
            } as React.SVGProps<SVGSVGElement>)}
            <span className="text-sm text-[#343A40]">{label}</span>
        </div>
    </button>
);

export default Overview;
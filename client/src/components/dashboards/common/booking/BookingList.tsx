import {useEffect, useState} from 'react';
import {format} from 'date-fns';
import {Loader2, Eye, Edit2, Ban, Search} from 'lucide-react';

// Components
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
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
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue,} from "@/components/ui/select";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow,} from "@/components/ui/table";
import {Label} from "@/components/ui/label";
import {ScrollArea} from "@/components/ui/scroll-area";
import {Badge} from "@/components/ui/badge";
import {Separator} from "@/components/ui/separator";

import {
    BookingListItem,
    BookingDetail,
    BookingStats,
    ApiResponse,
    BookingStatus,
    PaymentStatus,
    getAllBookings,
    getBookingStats,
    getBookingDetailById,
    updateBooking,
    deleteBooking
} from '@/hooks/bookings';
import {cn} from "@/lib/utils";

interface InfoSectionProps {
    title: string
    children: React.ReactNode
    className?: string
}

interface InfoItemProps {
    label: string
    value: React.ReactNode
    className?: string
}

const BookingList = () => {
    // State management
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [stats, setStats] = useState<ApiResponse<BookingStats> | null>(null);
    const [bookings, setBookings] = useState<BookingListItem[]>([]);
    const [filteredBookings, setFilteredBookings] = useState<BookingListItem[]>([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState<BookingStatus | 'all'>('all');

    // Dialog states
    const [viewDialogOpen, setViewDialogOpen] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [deactivateDialogOpen, setDeactivateDialogOpen] = useState(false);
    const [selectedBooking, setSelectedBooking] = useState<ApiResponse<BookingDetail> | null>(null);
    const [viewDialogLoading, setViewDialogLoading] = useState(false);

    // Edit form states
    const [editStatus, setEditStatus] = useState<BookingStatus>('pending');
    const [editPaymentStatus, setEditPaymentStatus] = useState<PaymentStatus>('pending');

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 2 * 60 * 1000); // Refresh every 2 minutes
        return () => clearInterval(interval);
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [statsData, bookingsData] = await Promise.all([
                getBookingStats(),
                getAllBookings()
            ]);
            if (bookingsData?.data) {
                setBookings(bookingsData.data);
                setFilteredBookings(bookingsData.data);
            }
            if (statsData) {
                setStats(statsData);
            }
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            setBookings([]);
            setFilteredBookings([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        let filtered = [...bookings];
        if (searchTerm) {
            filtered = filtered.filter(booking =>
                booking.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                booking.job_card_number.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }
        if (statusFilter !== 'all') {
            filtered = filtered.filter(booking => booking.status === statusFilter);
        }
        setFilteredBookings(filtered);
    }, [searchTerm, statusFilter, bookings]);

    const handleViewBooking = async (id: number) => {
        try {
            setViewDialogLoading(true);
            const details = await getBookingDetailById(id);
            setSelectedBooking(details);
            setViewDialogOpen(true);
        } catch (error) {
            console.error('Error fetching booking details:', error);
        } finally {
            setViewDialogLoading(false);
        }
    };

    const handleUpdateBooking = async () => {
        if (!selectedBooking) return;
        try {
            const updatedBooking = await updateBooking(selectedBooking.data.id, {
                status: editStatus,
                payment_status: editPaymentStatus
            });
            setBookings(prev => prev.map(booking =>
                booking.id === updatedBooking.id ? {
                    ...booking,
                    status: updatedBooking.status,
                    payment_status: updatedBooking.payment_status
                } : booking
            ));
            setEditDialogOpen(false);
            await fetchData(); // Refresh data
        } catch (error) {
            console.error('Error updating booking:', error);
        }
    };

    const handleDeactivateBooking = async () => {
        if (!selectedBooking) return;
        try {
            await deleteBooking(selectedBooking.data.id);
            await fetchData();
        } catch (error) {
            console.error('Error deactivating booking:', error);
        }
    };

    const getStatusBadgeVariant = (status: BookingStatus) => {
        switch (status) {
            case 'completed':
                return 'success';
            case 'in_progress':
                return 'info';
            case 'pending':
                return 'warning';
            case 'cancelled':
                return 'destructive';
            default:
                return 'outline';
        }
    };

    const getPaymentBadgeVariant = (status: PaymentStatus) => {
        switch (status) {
            case 'pending':
                return 'warning';
            case 'paid':
                return 'success';
            case 'failed':
                return 'destructive';
            case 'refunded':
                return 'secondary';
            default:
                return 'outline';
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <Loader2 className="h-8 w-8 animate-spin"/>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 bg-red-50 text-red-700 rounded-lg">
                <p>Error loading bookings data: {error}</p>
            </div>
        );
    }

    return (
        <div className="space-y-6 p-6">
            {/* Stats Overview */}
            {stats?.data && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle>Active Repairs</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-3xl font-bold">{stats.data.active_repairs}</div>
                            <p className="text-sm text-muted-foreground">Currently in progress</p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle>Pending</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-3xl font-bold">{stats.data.pending_repairs}</div>
                            <p className="text-sm text-muted-foreground">Awaiting start</p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle>Completed Today</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-3xl font-bold">{stats.data.completed_today}</div>
                            <p className="text-sm text-muted-foreground">Successfully completed</p>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Main Bookings Table */}
            <Card>
                <CardHeader>
                    <div className="flex justify-between items-center">
                        <CardTitle>Bookings</CardTitle>
                    </div>
                    <div className="flex space-x-4 mt-4">
                        <div className="relative flex-1">
                            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground"/>
                            <Input
                                placeholder="Search by customer or job card..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-8 max-w-sm"
                            />
                        </div>
                        <Select value={statusFilter}
                                onValueChange={(value: string) => setStatusFilter(value as BookingStatus | 'all')}>
                            <SelectTrigger className="w-[180px]">
                                <SelectValue placeholder="Filter by status"/>
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Status</SelectItem>
                                <SelectItem value="pending">Pending</SelectItem>
                                <SelectItem value="in_progress">In Progress</SelectItem>
                                <SelectItem value="completed">Completed</SelectItem>
                                <SelectItem value="cancelled">Cancelled</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Job Card</TableHead>
                                <TableHead>Customer</TableHead>
                                <TableHead>Service</TableHead>
                                <TableHead>Scheduled Date</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Payment</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {filteredBookings.map((booking) => (
                                <TableRow key={booking.id}>
                                    <TableCell className="font-medium">
                                        {booking.job_card_number}
                                    </TableCell>
                                    <TableCell>
                                        <div>
                                            <div className="font-medium">{booking.customer_name}</div>
                                            <div className="text-sm text-muted-foreground">
                                                {booking.preferred_contact}: {booking.customer_contact}
                                            </div>
                                        </div>
                                    </TableCell>
                                    <TableCell>{booking.service_name}</TableCell>
                                    <TableCell>
                                        {format(new Date(booking.scheduled_time), 'PPp')}
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant={getStatusBadgeVariant(booking.status)}>
                                            {booking.status}
                                        </Badge>
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant={getPaymentBadgeVariant(booking.payment_status)}>
                                            {booking.payment_status}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <div className="flex justify-end gap-2">
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => handleViewBooking(booking.id)}>
                                                <Eye className="h-4 w-4"/>
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={async () => {
                                                    try {
                                                        const details = await getBookingDetailById(booking.id);
                                                        setSelectedBooking(details);
                                                        setEditStatus(details.data.status);
                                                        setEditPaymentStatus(details.data.payment_status);
                                                        setEditDialogOpen(true);
                                                    } catch (error) {
                                                        console.error('Error fetching booking details:', error);
                                                    }
                                                }}>
                                                <Edit2 className="h-4 w-4"/>
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={async () => {
                                                    try {
                                                        const details = await getBookingDetailById(booking.id);
                                                        setSelectedBooking(details);
                                                        setDeactivateDialogOpen(true);
                                                    } catch (error) {
                                                        console.error('Error fetching booking details:', error);
                                                    }
                                                }}>
                                                <Ban className="h-4 w-4"/>
                                            </Button>
                                        </div>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {/* View Dialog */}
            <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
                <DialogContent className="max-w-3xl">
                    <DialogHeader>
                        <DialogTitle className="text-2xl">Booking Details</DialogTitle>
                        <DialogDescription className="text-base">Job Card: {selectedBooking?.data.job_card_number}</DialogDescription>
                    </DialogHeader>
                    {viewDialogLoading ? (
                        <div className="flex items-center justify-center p-8">
                            <Loader2 className="h-8 w-8 animate-spin" />
                        </div>
                    ) : selectedBooking ? (
                        <ScrollArea className="max-h-[80vh]">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
                                <InfoSection title="Customer Information">
                                    <InfoItem
                                        label="Name"
                                        value={`${selectedBooking.data.customer.user.first_name} ${selectedBooking.data.customer.user.last_name}`}
                                    />
                                    <InfoItem label="Email" value={selectedBooking.data.customer.user.email} />
                                    <InfoItem label="Phone" value={selectedBooking.data.customer.user.phone_number || "N/A"} />
                                    {selectedBooking.data.customer.company_name && (
                                        <InfoItem label="Company" value={selectedBooking.data.customer.company_name} />
                                    )}
                                </InfoSection>

                                <InfoSection title="Device Information">
                                    <InfoItem label="Device Type" value={selectedBooking.data.device.device_type} />
                                    <InfoItem
                                        label="Brand & Model"
                                        value={`${selectedBooking.data.device.brand} ${selectedBooking.data.device.model}`}
                                    />
                                    <InfoItem label="Serial Number" value={selectedBooking.data.device.serial_number} />
                                </InfoSection>

                                <InfoSection title="Service Details">
                                    <InfoItem label="Service" value={selectedBooking.data.detailed_service.service.name} />
                                    <InfoItem label="Description" value={selectedBooking.data.detailed_service.changes_to_make} />
                                    <InfoItem label="Estimated Time" value={selectedBooking.data.detailed_service.service.estimated_time} />
                                    <InfoItem
                                        label="Status"
                                        value={
                                            <Badge variant={getStatusBadgeVariant(selectedBooking.data.status)}>
                                                {selectedBooking.data.status}
                                            </Badge>
                                        }
                                    />
                                    <InfoItem
                                        label="Payment Status"
                                        value={
                                            <Badge variant={getPaymentBadgeVariant(selectedBooking.data.payment_status)}>
                                                {selectedBooking.data.payment_status}
                                            </Badge>
                                        }
                                    />
                                </InfoSection>

                                <InfoSection title="Financial Details">
                                    <InfoItem
                                        label="Service Cost"
                                        value={`KES ${selectedBooking.data.detailed_service.price.toLocaleString()}`}
                                    />
                                    {selectedBooking.data.parts_used.length > 0 && (
                                        <>
                                            <Separator className="my-2" />
                                            <h4 className="font-semibold text-base mb-2">Inventory Parts Used</h4>
                                            {selectedBooking.data.parts_used.map((part, index) => (
                                                <InfoItem
                                                    key={index}
                                                    label={`${part.part.name} x${part.quantity}`}
                                                    value={`KES ${part.total_cost.toLocaleString()}`}
                                                    className="text-sm"
                                                />
                                            ))}
                                        </>
                                    )}
                                    <InfoItem
                                        label="Total Parts Cost"
                                        value={`KES ${selectedBooking.data.total_parts_cost.toLocaleString()}`}
                                    />
                                    <InfoItem
                                        label="Grand Total"
                                        value={`KES ${selectedBooking.data.total_cost.toLocaleString()}`}
                                        className="font-semibold text-base"
                                    />
                                </InfoSection>

                                <InfoSection title="Additional Information" className="col-span-full">
                                    <InfoItem
                                        label="Diagnosis"
                                        value={selectedBooking.data.diagnosis || "No diagnosis provided yet"}
                                        className="bg-muted p-3 rounded-md whitespace-pre-wrap"
                                    />
                                    <InfoItem
                                        label="Notes"
                                        value={selectedBooking.data.notes || "No additional notes"}
                                        className="bg-muted p-3 rounded-md whitespace-pre-wrap"
                                    />
                                    <div className="space-y-2">
                                        <h4 className="font-semibold text-base">Timeline</h4>
                                        <InfoItem
                                            label="Created"
                                            value={format(new Date(selectedBooking.data.created_at), "PPp")}
                                            className="flex justify-between"
                                        />
                                        <InfoItem
                                            label="Last Updated"
                                            value={format(new Date(selectedBooking.data.updated_at), "PPp")}
                                            className="flex justify-between"
                                        />
                                    </div>
                                </InfoSection>
                            </div>
                        </ScrollArea>
                    ) : null}
                </DialogContent>
            </Dialog>

            {/* Edit Dialog */}
            <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Update Booking Status</DialogTitle>
                        <DialogDescription>
                            Modify the status for job card {selectedBooking?.data.job_card_number}
                        </DialogDescription>
                    </DialogHeader>

                    <div className="grid gap-6 py-4">
                        <div className="space-y-2">
                            <Label htmlFor="status">Booking Status</Label>
                            <Select
                                value={editStatus}
                                onValueChange={(value: BookingStatus) => setEditStatus(value)}>
                                <SelectTrigger id="status">
                                    <SelectValue placeholder="Select status"/>
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="pending">Pending</SelectItem>
                                    <SelectItem value="confirmed">Confirmed</SelectItem>
                                    <SelectItem value="in_progress">In Progress</SelectItem>
                                    <SelectItem value="completed">Completed</SelectItem>
                                    <SelectItem value="cancelled">Cancelled</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="payment">Payment Status</Label>
                            <Select value={editPaymentStatus}
                                    onValueChange={(value: PaymentStatus) => setEditPaymentStatus(value)}>
                                <SelectTrigger id="payment">
                                    <SelectValue placeholder="Select payment status"/>
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="pending">Pending</SelectItem>
                                    <SelectItem value="paid">Paid</SelectItem>
                                    <SelectItem value="failed">Failed</SelectItem>
                                    <SelectItem value="refunded">Refunded</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <DialogFooter>
                        <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleUpdateBooking}>
                            Update Booking
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Deactivate Dialog */}
            <AlertDialog open={deactivateDialogOpen} onOpenChange={setDeactivateDialogOpen}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Deactivate Booking</AlertDialogTitle>
                        <AlertDialogDescription>
                            Are you sure you want to deactivate job card {selectedBooking?.data.job_card_number}?
                            This booking will be marked as inactive but its records will be preserved.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={handleDeactivateBooking}>
                            Deactivate
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
};

// eslint-disable-next-line react/prop-types
const InfoSection: React.FC<InfoSectionProps> = ({ title, children, className }) => {
    return (
        <div className={cn("space-y-4", className)}>
            <h3 className="font-semibold text-lg border-b pb-2">{title}</h3>
            <div className="space-y-2">{children}</div>
        </div>
    )
}

// eslint-disable-next-line react/prop-types
const InfoItem: React.FC<InfoItemProps> = ({ label, value, className }) => {
    return (
        <div className={cn("space-y-1", className)}>
            <div className="font-medium text-sm text-muted-foreground">{label}</div>
            <div className="text-sm">{value}</div>
        </div>
    )
}

export default BookingList;
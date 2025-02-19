import {Tabs, TabsContent, TabsList, TabsTrigger} from "@/components/ui/tabs"
import BookingList from "@/components/dashboards/common/booking/BookingList"
import NewBooking from "@/components/dashboards/common/booking/NewBooking"

const BookingsView = () => {
    return (
        <Tabs defaultValue="existing" className="w-full">
            <TabsList className="grid w-full grid-cols-2 h-11 items-stretch bg-muted p-1 rounded-md">
                <TabsTrigger
                    value="existing"
                    className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-none rounded-sm transition-colors">
                    Existing Bookings
                </TabsTrigger>
                <TabsTrigger
                    value="new"
                    className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-none rounded-sm transition-colors">
                    Create New Booking
                </TabsTrigger>
            </TabsList>
            <TabsContent value="existing">
                <BookingList/>
            </TabsContent>
            <TabsContent value="new">
                <NewBooking/>
            </TabsContent>
        </Tabs>
    )
}

export default BookingsView


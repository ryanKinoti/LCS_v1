import {useState} from "react"
import {Button} from "@/components/ui/button"
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card"
import {Input} from "@/components/ui/input"
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select"
import {RadioGroup, RadioGroupItem} from "@/components/ui/radio-group"
import {useToast} from "@/hooks/use-toast"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from "@/components/ui/form"
import {Loader2} from "lucide-react"
import * as z from "zod"
import {useFieldArray, useForm} from "react-hook-form"
import {zodResolver} from "@hookform/resolvers/zod"
import {
    CustomerFormData,
    DeviceFormData,
    BookingFormData,
    CustomerProfile,
    Device,
    DetailedService,
    findCustomerByEmail,
    createCustomer,
    createDevice,
    initiateBooking,
    getDetailedServices, DevicePartFormData, addDeviceParts
} from '@/hooks/bookings.ts'

const customerTypeSchema = z.object({
    type: z.enum(["existing", "new"]),
    email: z.string().email("Invalid email address"),
    firstName: z.string().optional(),
    lastName: z.string().optional(),
    phoneNumber: z.string().optional(),
    preferredContact: z.enum(["email", "phone"]).optional(),
})

const deviceSchema = z.object({
    deviceType: z.string().min(1, "Device type is required"),
    brand: z.string().min(1, "Brand is required"),
    model: z.string().min(1, "Model is required"),
    serialNumber: z.string().min(1, "Serial number is required"),
})

const devicePartSchema = z.object({
    parts: z.array(z.object({
        name: z.string().min(1, "Part name is required"),
        model: z.string().min(1, "Model is required"),
        serial_number: z.string().min(5, "Serial number must be at least 5 characters"),
        category: z.string().min(1, "Category is required"),
        warranty_months: z.number().min(0, "Warranty months must be 0 or greater"),
    }))
});

const bookingSchema = z.object({
    serviceId: z.string().min(1, "Service is required"),
    scheduledTime: z.string().min(1, "Scheduled time is required"),
    notes: z.string().optional(),
})

const NewBooking = () => {
    const [currentStep, setCurrentStep] = useState(0)
    const [loading, setLoading] = useState(false)
    const [customerData, setCustomerData] = useState<CustomerProfile | null>(null)
    const [deviceData, setDeviceData] = useState<Device | null>(null)
    const [deviceParts, setDeviceParts] = useState<DevicePartFormData[]>([]);
    const [services, setServices] = useState<DetailedService[]>([])
    const {toast} = useToast()

    const customerForm = useForm<CustomerFormData>({
        resolver: zodResolver(customerTypeSchema),
        defaultValues: {
            type: "existing",
            email: "",
            firstName: "",
            lastName: "",
            phoneNumber: "",
            preferredContact: "email",
        },
    })

    const deviceForm = useForm<DeviceFormData>({
        resolver: zodResolver(deviceSchema),
        defaultValues: {
            deviceType: "",
            brand: "",
            model: "",
            serialNumber: "",
        },
    })

    const devicePartsForm = useForm<{ parts: DevicePartFormData[] }>({
        resolver: zodResolver(devicePartSchema),
        defaultValues: {
            parts: [
                {
                    name: "",
                    model: "",
                    serial_number: "",
                    category: "",
                    warranty_months: 0,
                    status: "used"
                }
            ]
        }
    });

    const bookingForm = useForm<BookingFormData>({
        resolver: zodResolver(bookingSchema),
        defaultValues: {
            serviceId: "",
            scheduledTime: "",
            notes: "",
        },
    })

    useState(() => {
        const loadServices = async () => {
            try {
                const response = await getDetailedServices();
                setServices(response.data);
            } catch (error: unknown) {
                if (error instanceof Error) {
                    toast({
                        title: "Error",
                        description: error.message,
                        variant: "destructive",
                    })
                }
            }
        };
        loadServices();
    });

    const handleCustomerSubmit = async (data: CustomerFormData) => {
        setLoading(true)
        try {
            let customerResponse;
            if (data.type === "new") {
                customerResponse = await createCustomer(data);
                toast({
                    title: "Temporary Account Created",
                    description: `Temporary password: ${customerResponse.message}. Please inform the customer.`,
                })
            } else {
                customerResponse = await findCustomerByEmail(data.email);
            }

            setCustomerData(customerResponse.data)
            setCurrentStep(1)
        } catch (error) {
            if (error instanceof Error) {
                toast({
                    title: "Error",
                    description: error.message,
                    variant: "destructive",
                })
            }
        } finally {
            setLoading(false)
        }
    }

    const handleDeviceSubmit = async (data: DeviceFormData) => {
        if (!customerData) return;

        setLoading(true)
        try {
            const deviceResponse = await createDevice(data, customerData.id)
            setDeviceData(deviceResponse.data)
            setCurrentStep(2)
        } catch (error) {
            if (error instanceof Error) {
                toast({
                    title: "Error",
                    description: error.message,
                    variant: "destructive",
                })
            }
        } finally {
            setLoading(false)
        }
    }

    const handleDevicePartsSubmit = async (data: { parts: DevicePartFormData[] }) => {
        if (!deviceData) return;

        setLoading(true);
        try {
            const response = await addDeviceParts(deviceData.id, data.parts);
            setDeviceParts(response.data);
            setCurrentStep(3); // Move to booking step
        } catch (error) {
            if (error instanceof Error) {
                toast({
                    title: "Error",
                    description: error.message,
                    variant: "destructive",
                });
            }
        } finally {
            setLoading(false);
        }
    };

    const handleBookingSubmit = async (data: BookingFormData) => {
        if (!customerData || !deviceData) return;

        setLoading(true)
        try {
            await initiateBooking(data, customerData.id, deviceData.id);

            toast({
                title: "Success",
                description: "Booking created successfully",
            })
            customerForm.reset()
            deviceForm.reset()
            bookingForm.reset()
            setCurrentStep(0)
            setCustomerData(null)
            setDeviceData(null)
        } catch (error) {
            if (error instanceof Error) {
                toast({
                    title: "Error",
                    description: error.message,
                    variant: "destructive",
                })
            }
        } finally {
            setLoading(false)
        }
    }

    const renderCustomerStep = () => (
        <Form {...customerForm}>
            <form onSubmit={customerForm.handleSubmit(handleCustomerSubmit)} className="space-y-6">
                <FormField
                    control={customerForm.control}
                    name="type"
                    render={({field}) => (
                        <FormItem className="space-y-3">
                            <FormLabel>Customer Type</FormLabel>
                            <FormControl>
                                <RadioGroup
                                    onValueChange={field.onChange}
                                    defaultValue={field.value}
                                    className="flex flex-col space-y-1"
                                >
                                    <FormItem className="flex items-center space-x-3 space-y-0">
                                        <FormControl>
                                            <RadioGroupItem value="existing"/>
                                        </FormControl>
                                        <FormLabel className="font-normal">
                                            Existing Customer
                                        </FormLabel>
                                    </FormItem>
                                    <FormItem className="flex items-center space-x-3 space-y-0">
                                        <FormControl>
                                            <RadioGroupItem value="new"/>
                                        </FormControl>
                                        <FormLabel className="font-normal">
                                            New Customer
                                        </FormLabel>
                                    </FormItem>
                                </RadioGroup>
                            </FormControl>
                        </FormItem>
                    )}
                />

                <FormField
                    control={customerForm.control}
                    name="email"
                    render={({field}) => (
                        <FormItem>
                            <FormLabel>Email</FormLabel>
                            <FormControl>
                                <Input {...field} type="email" placeholder="Email address"/>
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}
                />

                {customerForm.watch("type") === "new" && (
                    <>
                        <FormField
                            control={customerForm.control}
                            name="firstName"
                            render={({field}) => (
                                <FormItem>
                                    <FormLabel>First Name</FormLabel>
                                    <FormControl>
                                        <Input {...field} placeholder="First name"/>
                                    </FormControl>
                                    <FormMessage/>
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={customerForm.control}
                            name="lastName"
                            render={({field}) => (
                                <FormItem>
                                    <FormLabel>Last Name</FormLabel>
                                    <FormControl>
                                        <Input {...field} placeholder="Last name"/>
                                    </FormControl>
                                    <FormMessage/>
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={customerForm.control}
                            name="phoneNumber"
                            render={({field}) => (
                                <FormItem>
                                    <FormLabel>Phone Number</FormLabel>
                                    <FormControl>
                                        <Input {...field} placeholder="Phone number"/>
                                    </FormControl>
                                    <FormMessage/>
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={customerForm.control}
                            name="preferredContact"
                            render={({field}) => (
                                <FormItem>
                                    <FormLabel>Preferred Contact Method</FormLabel>
                                    <Select
                                        onValueChange={field.onChange}
                                        defaultValue={field.value}
                                    >
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select preferred contact"/>
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            <SelectItem value="email">Email</SelectItem>
                                            <SelectItem value="phone">Phone</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <FormMessage/>
                                </FormItem>
                            )}
                        />
                    </>
                )}

                <Button type="submit" disabled={loading}>
                    {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin"/>}
                    Next
                </Button>
            </form>
        </Form>
    )

    const renderDeviceStep = () => (
        <Form {...deviceForm}>
            <form onSubmit={deviceForm.handleSubmit(handleDeviceSubmit)} className="space-y-6">
                <FormField
                    control={deviceForm.control}
                    name="deviceType"
                    render={({field}) => (
                        <FormItem>
                            <FormLabel>Device Type</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                                <FormControl>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select device type"/>
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                    <SelectItem value="laptop">Laptop</SelectItem>
                                    <SelectItem value="desktop">Desktop</SelectItem>
                                    <SelectItem value="printer">Printer</SelectItem>
                                </SelectContent>
                            </Select>
                            <FormMessage/>
                        </FormItem>
                    )}
                />

                <FormField
                    control={deviceForm.control}
                    name="brand"
                    render={({field}) => (
                        <FormItem>
                            <FormLabel>Brand</FormLabel>
                            <FormControl>
                                <Input {...field} placeholder="Device brand"/>
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}
                />

                <FormField
                    control={deviceForm.control}
                    name="model"
                    render={({field}) => (
                        <FormItem>
                            <FormLabel>Model</FormLabel>
                            <FormControl>
                                <Input {...field} placeholder="Device model"/>
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}
                />

                <FormField
                    control={deviceForm.control}
                    name="serialNumber"
                    render={({field}) => (
                        <FormItem>
                            <FormLabel>Serial Number</FormLabel>
                            <FormControl>
                                <Input {...field} placeholder="Device serial number"/>
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}
                />

                <div className="flex justify-between">
                    <Button type="button" variant="outline" onClick={() => setCurrentStep(0)}>
                        Previous
                    </Button>
                    <Button type="submit" disabled={loading}>
                        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin"/>}
                        Next
                    </Button>
                </div>
            </form>
        </Form>
    )

    const renderDevicePartsStep = () => {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const {fields, append, remove} = useFieldArray({
            control: devicePartsForm.control,
            name: "parts"
        });

        return (
            <Form {...devicePartsForm}>
                <form onSubmit={devicePartsForm.handleSubmit(handleDevicePartsSubmit)} className="space-y-6">
                    <div className="space-y-4">
                        {fields.map((field, index) => (
                            <div key={field.id} className="p-4 border rounded-lg space-y-4">
                                <div className="flex justify-between items-center">
                                    <h4 className="font-medium">Part {index + 1}</h4>
                                    {fields.length > 1 && (
                                        <Button
                                            type="button"
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => remove(index)}
                                        >
                                            Remove
                                        </Button>
                                    )}
                                </div>

                                <FormField
                                    control={devicePartsForm.control}
                                    name={`parts.${index}.name`}
                                    render={({field}) => (
                                        <FormItem>
                                            <FormLabel>Part Name</FormLabel>
                                            <FormControl>
                                                <Input {...field} placeholder="e.g. 16GB DDR4 RAM"/>
                                            </FormControl>
                                            <FormMessage/>
                                        </FormItem>
                                    )}
                                />

                                <FormField
                                    control={devicePartsForm.control}
                                    name={`parts.${index}.model`}
                                    render={({field}) => (
                                        <FormItem>
                                            <FormLabel>Model Number</FormLabel>
                                            <FormControl>
                                                <Input {...field} placeholder="Model number"/>
                                            </FormControl>
                                            <FormMessage/>
                                        </FormItem>
                                    )}
                                />

                                <FormField
                                    control={devicePartsForm.control}
                                    name={`parts.${index}.serial_number`}
                                    render={({field}) => (
                                        <FormItem>
                                            <FormLabel>Serial Number</FormLabel>
                                            <FormControl>
                                                <Input {...field} placeholder="Serial number"/>
                                            </FormControl>
                                            <FormMessage/>
                                        </FormItem>
                                    )}
                                />

                                <FormField
                                    control={devicePartsForm.control}
                                    name={`parts.${index}.category`}
                                    render={({field}) => (
                                        <FormItem>
                                            <FormLabel>Category</FormLabel>
                                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                                                <FormControl>
                                                    <SelectTrigger>
                                                        <SelectValue placeholder="Select category"/>
                                                    </SelectTrigger>
                                                </FormControl>
                                                <SelectContent>
                                                    {Object.entries(DeviceParts.DEVICE_PARTS_CHOICES).map(([key, value]) => (
                                                        <SelectItem key={key} value={key}>
                                                            {value}
                                                        </SelectItem>
                                                    ))}
                                                </SelectContent>
                                            </Select>
                                            <FormMessage/>
                                        </FormItem>
                                    )}
                                />

                                <FormField
                                    control={devicePartsForm.control}
                                    name={`parts.${index}.warranty_months`}
                                    render={({field}) => (
                                        <FormItem>
                                            <FormLabel>Warranty (months)</FormLabel>
                                            <FormControl>
                                                <Input
                                                    {...field}
                                                    type="number"
                                                    min="0"
                                                    onChange={e => field.onChange(parseInt(e.target.value))}
                                                />
                                            </FormControl>
                                            <FormMessage/>
                                        </FormItem>
                                    )}
                                />
                            </div>
                        ))}
                    </div>

                    <Button
                        type="button"
                        variant="outline"
                        className="w-full"
                        onClick={() => append({
                            name: "",
                            model: "",
                            serial_number: "",
                            category: "",
                            warranty_months: 0,
                            status: "used"
                        })}
                    >
                        Add Another Part
                    </Button>

                    <div className="flex justify-between">
                        <Button type="button" variant="outline" onClick={() => setCurrentStep(1)}>
                            Previous
                        </Button>
                        <Button type="submit" disabled={loading}>
                            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin"/>}
                            Next
                        </Button>
                    </div>
                </form>
            </Form>
        );
    };

    const renderBookingStep = () => (
        <Form {...bookingForm}>
            <form onSubmit={bookingForm.handleSubmit(handleBookingSubmit)} className="space-y-6">
                <FormField
                    control={bookingForm.control}
                    name="serviceId"
                    render={({field}) => (
                        <FormItem>
                            <FormLabel>Service</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                                <FormControl>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select service"/>
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                    <SelectItem value="1">Screen Repair</SelectItem>
                                    <SelectItem value="2">Battery Replacement</SelectItem>
                                    <SelectItem value="3">OS Installation</SelectItem>
                                </SelectContent>
                            </Select>
                            <FormMessage/>
                        </FormItem>
                    )}
                />

                <FormField
                    control={bookingForm.control}
                    name="scheduledTime"
                    render={({field}) => (
                        <FormItem>
                            <FormLabel>Scheduled Time</FormLabel>
                            <FormControl>
                                <Input {...field} type="datetime-local"/>
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}
                />

                <FormField
                    control={bookingForm.control}
                    name="notes"
                    render={({field}) => (
                        <FormItem>
                            <FormLabel>Notes</FormLabel>
                            <FormControl>
                                <Input {...field} placeholder="Additional notes"/>
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}
                />

                <div className="flex justify-between">
                    <Button type="button" variant="outline" onClick={() => setCurrentStep(1)}>
                        Previous
                    </Button>
                    <Button type="submit" disabled={loading}>
                        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin"/>}
                        Create Booking
                    </Button>
                </div>
            </form>
        </Form>
    )

    return (
        <Card className="w-full max-w-3xl mx-auto">
            <CardHeader>
                <CardTitle>
                    {currentStep === 0 && "Step 1: Customer Information"}
                    {currentStep === 1 && "Step 2: Device Information"}
                    {currentStep === 2 && "Step 3: Device Parts"}
                    {currentStep === 3 && "Step 4: Booking Details"}
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="mb-8">
                    <div className="flex justify-between mb-2">
                        {["Customer", "Device", "Device Parts", "Booking"].map((step, index) => (
                            <div
                                key={step}
                                className="flex items-center">
                                <div
                                    className={`w-8 h-8 rounded-full flex items-center justify-center ${
                                        index <= currentStep
                                            ? "bg-primary text-primary-foreground"
                                            : "bg-muted text-muted-foreground"
                                    }`}>
                                    {index + 1}
                                </div>
                                <span
                                    className={`ml-2 ${
                                        index <= currentStep
                                            ? "text-primary"
                                            : "text-muted-foreground"
                                    }`}>
                                    {step}
                                </span>
                                {index < 3 && (
                                    <div
                                        className={`w-16 h-0.5 mx-2 ${
                                            index < currentStep ? "bg-primary" : "bg-muted"
                                        }`}
                                    />
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {currentStep === 0 && (
                    <div>
                        <p className="text-sm text-muted-foreground mb-6">
                            Enter customer details. For new customers, a temporary account will be created
                            with a generated password.
                        </p>
                        {renderCustomerStep()}
                    </div>
                )}

                {currentStep === 1 && (
                    <div>
                        <p className="text-sm text-muted-foreground mb-6">
                            Enter the details of the device that needs service. This information will be
                            used to track the device throughout the repair process.
                        </p>
                        {renderDeviceStep()}
                    </div>
                )}

                {currentStep === 2 && (
                    <div>
                        <p className="text-sm text-muted-foreground mb-6">
                            Register the parts that came with or are currently installed in the device.
                            This information helps us track and manage device components throughout the repair process.
                        </p>
                        {renderDevicePartsStep()}
                    </div>
                )}

                {currentStep === 3 && (
                    <div>
                        <p className="text-sm text-muted-foreground mb-6">
                            Select the service required and schedule the appointment. Make sure to check
                            the available time slots and add any relevant notes.
                        </p>
                        {renderBookingStep()}
                    </div>
                )}
            </CardContent>
        </Card>
    )
}

export default NewBooking
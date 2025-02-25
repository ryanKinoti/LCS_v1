import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {Button} from "@/components/ui/button";
import {AlertTriangle, AlertCircle, CheckCircle, Info} from "lucide-react";
import {useModal} from "@/contexts/ModalContext";
import {ModalType} from "@/lib/types/constants/declarations";

export const Modal = () => {
    const {currentModal, closeModal} = useModal();

    if (!currentModal) return null;

    const renderModalContent = () => {
        switch (currentModal.type) {
            case ModalType.CONFIRMATION:
                return (
                    <>
                        <DialogHeader>
                            <DialogTitle>{currentModal.title}</DialogTitle>
                            {currentModal.description && (
                                <DialogDescription>{currentModal.description}</DialogDescription>
                            )}
                        </DialogHeader>
                        <DialogFooter className="sm:justify-end">
                            <Button
                                variant="outline"
                                onClick={closeModal}
                            >
                                {currentModal.cancelLabel || 'Cancel'}
                            </Button>
                            <Button
                                variant={currentModal.isDangerous ? "destructive" : "default"}
                                onClick={() => {
                                    currentModal.onConfirm();
                                    closeModal();
                                }}
                            >
                                {currentModal.confirmLabel || 'Confirm'}
                            </Button>
                        </DialogFooter>
                    </>
                );

            case ModalType.FORM:
                return (
                    <>
                        <DialogHeader>
                            <DialogTitle>{currentModal.title}</DialogTitle>
                            {currentModal.description && (
                                <DialogDescription>{currentModal.description}</DialogDescription>
                            )}
                        </DialogHeader>
                        <div className="py-4">{currentModal.formContent}</div>
                        <DialogFooter className="sm:justify-end">
                            <Button
                                variant="outline"
                                onClick={closeModal}
                            >
                                Cancel
                            </Button>
                            <Button
                                onClick={() => {
                                    currentModal.onSubmit();
                                    closeModal();
                                }}
                            >
                                {currentModal.submitLabel || 'Submit'}
                            </Button>
                        </DialogFooter>
                    </>
                );

            case ModalType.ALERT:
                { let Icon = Info;
                let iconClass = "text-blue-500";

                if (currentModal.alertType === "warning") {
                    Icon = AlertTriangle;
                    iconClass = "text-amber-500";
                } else if (currentModal.alertType === "error") {
                    Icon = AlertCircle;
                    iconClass = "text-red-500";
                } else if (currentModal.alertType === "success") {
                    Icon = CheckCircle;
                    iconClass = "text-green-500";
                }

                return (
                    <>
                        <DialogHeader className="flex flex-row items-center gap-4">
                            <Icon className={`h-6 w-6 ${iconClass}`}/>
                            <div>
                                <DialogTitle>{currentModal.title}</DialogTitle>
                                {currentModal.description && (
                                    <DialogDescription>{currentModal.description}</DialogDescription>
                                )}
                            </div>
                        </DialogHeader>
                        <DialogFooter className="sm:justify-end">
                            <Button onClick={closeModal}>
                                OK
                            </Button>
                        </DialogFooter>
                    </>
                ); }

            case ModalType.CUSTOM:
                return (
                    <>
                        <DialogHeader>
                            <DialogTitle>{currentModal.title}</DialogTitle>
                            {currentModal.description && (
                                <DialogDescription>{currentModal.description}</DialogDescription>
                            )}
                        </DialogHeader>
                        <div className="py-4">{currentModal.content}</div>
                        <DialogFooter className="sm:justify-end">
                            <Button onClick={closeModal}>
                                Close
                            </Button>
                        </DialogFooter>
                    </>
                );

            default:
                return null;
        }
    };

    return (
        <Dialog open={!!currentModal} onOpenChange={(open) => !open && closeModal()}>
            <DialogContent className="sm:max-w-md">
                {renderModalContent()}
            </DialogContent>
        </Dialog>
    );
};
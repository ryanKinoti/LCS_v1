import {createContext, useContext, useState} from "react";
import {
    AlertModalProps,
    ConfirmationModalProps, CustomModalProps,
    FormModalProps,
    ModalContextType, ModalProps,
    ModalProviderProps
} from "@/lib/types/interfaces/common.ts";

const ModalContext = createContext<ModalContextType | undefined>(undefined);

export const ModalProvider: React.FC<ModalProviderProps> = ({children}) => {
    const [currentModal, setCurrentModal] = useState<ModalProps | null>(null);

    const closeModal = () => {
        setCurrentModal(null);
    };
    const showConfirmationModal = (props: Omit<ConfirmationModalProps, 'type'>) => {
        setCurrentModal({...props, type: 'confirmation'});
    };
    const showFormModal = (props: Omit<FormModalProps, 'type'>) => {
        setCurrentModal({...props, type: 'form'});
    };

    // Show alert modal
    const showAlertModal = (props: Omit<AlertModalProps, 'type'>) => {
        setCurrentModal({...props, type: 'alert'});
    };

    // Show custom modal
    const showCustomModal = (props: Omit<CustomModalProps, 'type'>) => {
        setCurrentModal({...props, type: 'custom'});
    };

    // Context value
    const contextValue: ModalContextType = {
        currentModal,
        showConfirmationModal,
        showFormModal,
        showAlertModal,
        showCustomModal,
        closeModal,
    };

    return (
        <ModalContext.Provider value={contextValue}>
            {children}
            {/* The Modal component will be implemented separately to render the actual UI */}
        </ModalContext.Provider>
    );
};

export const useModal = (): ModalContextType => {
    const context = useContext(ModalContext);
    if (!context) {
        throw new Error('useModal must be used within a ModalProvider');
    }
    return context;
};

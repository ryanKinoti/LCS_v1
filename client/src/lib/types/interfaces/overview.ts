import {ReactElement} from "react";

export interface StatCardProps {
    title: string;
    value: number | string;
    icon: ReactElement;
    color: string;
    subtitle?: string;
}

export interface QuickActionButtonProps {
    icon: ReactElement;
    label: string;
    onClick: () => void;
}
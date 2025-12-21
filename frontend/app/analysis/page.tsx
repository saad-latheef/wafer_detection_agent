"use client";

import { WaferDetectionDashboard } from "@/components/wafer-detection-dashboard";
import { AppSidebar } from "@/components/layout/AppSidebar";
import { cn } from "@/lib/utils";

export default function AnalysisPage() {
    return (
        <>
            <AppSidebar showBackButton={true} currentPage="dashboard" />
            <div className={cn("transition-all duration-300", "ml-64")}>
                <WaferDetectionDashboard />
            </div>
        </>
    );
}

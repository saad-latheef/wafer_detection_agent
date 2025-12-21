"use client";

import { WaferDetectionDashboard } from "@/components/wafer-detection-dashboard";
import { PageTransition } from "@/components/layout/PageTransition";
import { cn } from "@/lib/utils";

export default function AnalysisPage() {
    return (
        <PageTransition>
            <div className={cn("transition-all duration-300", "ml-64")}>
                <WaferDetectionDashboard />
            </div>
        </PageTransition>
    );
}

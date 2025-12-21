"use client";

import { WaferDetectionDashboard } from "@/components/wafer-detection-dashboard";
import { useRouter } from "next/navigation";

export default function AnalysisPage() {
    const router = useRouter();

    return (
        <div className="min-h-screen bg-background-darker">
            <WaferDetectionDashboard onBack={() => router.push("/")} />
        </div>
    );
}
